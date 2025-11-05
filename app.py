import os, csv, time
from collections import deque
from threading import Thread, Event
from datetime import datetime
import psutil

from flask import (
    Flask, render_template, jsonify, request, redirect, session,
    send_file, url_for
)
from werkzeug.security import check_password_hash
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST
from functools import wraps

from config import Config

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

# ---------------- State ----------------
stop_evt = Event()
HISTORY_POINTS = 2000
history = deque(maxlen=HISTORY_POINTS)
latest = {}              # latest point for /data
pending_rows = []        # buffer for batched CSV writes
_sampler_started = False # start-once guard

# ---------------- Helpers ----------------
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def ensure_csv_header(path):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            csv.writer(f).writerow(["ts","cpu","mem","disk","bytes_sent","bytes_recv"])

def rotate_csv(path, max_mb=10):
    if not os.path.exists(path):
        return
    size_mb = os.stat(path).st_size / (1024*1024)
    if size_mb >= max_mb:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        os.replace(path, f"{path.rstrip('.csv')}-{ts}.csv")
        ensure_csv_header(path)

# Never cache API responses
@app.after_request
def add_no_cache_headers(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp

# ---------------- Sampler (runs in background) ----------------
def sampler_loop():
    """Collect metrics on a fixed cadence and keep them in memory + CSV."""
    ensure_csv_header(app.config["CSV_PATH"])

    # warm-up for non-blocking cpu_percent
    psutil.cpu_percent(None)

    interval = app.config["SAMPLE_INTERVAL_SEC"]
    flush_every = 10
    counter = 0
    last_alert = 0.0
    alert_cooldown = app.config["ALERT_COOLDOWN_SEC"]

    while not stop_evt.is_set():
        ts = int(time.time())
        cpu = psutil.cpu_percent(None)  # non-blocking
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        net = psutil.net_io_counters()

        point = {
            "ts": ts, "cpu": cpu, "mem": mem, "disk": disk,
            "bytes_sent": net.bytes_sent, "bytes_recv": net.bytes_recv
        }

        # update in-memory
        latest.update(point)
        history.append(point)

        # buffer CSV write
        pending_rows.append([ts, cpu, mem, disk, net.bytes_sent, net.bytes_recv])
        counter += 1

        # debug every 5th sample so you know it's running
        if counter % 5 == 0:
            print(f"[SAMPLE] cpu={cpu:.1f}% mem={mem:.1f}% disk={disk:.1f}%")

        # simple alert with cooldown
        if max(cpu, mem, disk) > max(app.config["CPU_THRESH"], app.config["MEM_THRESH"], app.config["DISK_THRESH"]):
            now = time.time()
            if now - last_alert > alert_cooldown:
                print(f"[ALERT] {datetime.now().isoformat()} CPU={cpu} MEM={mem} DISK={disk}")
                last_alert = now

        # periodic flush & rotation
        if counter % flush_every == 0 and pending_rows:
            rotate_csv(app.config["CSV_PATH"], max_mb=app.config.get("CSV_MAX_MB", 10))
            with open(app.config["CSV_PATH"], "a", newline="") as f:
                csv.writer(f).writerows(pending_rows)
            pending_rows.clear()

        time.sleep(interval)

# Flask 3: start the sampler the first time any request hits (run once)
@app.before_request
def _start_sampler_once():
    global _sampler_started
    if not _sampler_started:
        _sampler_started = True
        print("[BOOT] starting sampler thread")
        Thread(target=sampler_loop, daemon=True).start()

# ---------------- Auth ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = (request.form.get("username") or "").strip()
        p = (request.form.get("password") or "").strip()

        if not u or not p:
            return render_template("login.html", error_msg="Please enter username and password.")

        ok_user = (u == app.config["ADMIN_USER"])
        ok_pass = check_password_hash(app.config["ADMIN_HASH"], p)
        print("[LOGIN]", "user_ok=", ok_user, "pass_ok=", ok_pass, "u=", repr(u))  # TEMP debug

        if ok_user and ok_pass:
            session["logged_in"] = True
            return redirect(url_for("index"))

        return render_template("login.html", error_msg="Invalid username or password.")

    if session.get("logged_in"):
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- Pages & APIs ----------------
@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/data")
@login_required
def data():
    if not latest:
        return jsonify(status="WarmingUp")
    cpu = float(latest.get("cpu", 0))
    mem = float(latest.get("mem", 0))
    disk = float(latest.get("disk", 0))
    status = "OK"
    if max(cpu, mem, disk) > 90: status = "Critical"
    elif max(cpu, mem, disk) > 80: status = "Warning"
    return jsonify(
        cpu=cpu, mem=mem, disk=disk,
        uptime=psutil.boot_time(),
        net={"bytes_sent": int(latest.get("bytes_sent", 0)), "bytes_recv": int(latest.get("bytes_recv", 0))},
        status=status
    )

@app.route("/history")
@login_required
def history_api():
    n = int(request.args.get("n", 200))
    rows = list(history)[-n:]
    return jsonify(rows=rows)

@app.route("/top")
@login_required
def top():
    limit = int(request.args.get("limit", 10))
    procs = []
    for p in psutil.process_iter(["pid","name","username","cpu_percent","memory_percent"]):
        info = p.info
        info["cpu_percent"] = info.get("cpu_percent") or 0.0
        info["memory_percent"] = round((info.get("memory_percent") or 0.0), 2)
        procs.append(info)
    procs.sort(key=lambda x: x["cpu_percent"], reverse=True)
    return jsonify(top_cpu=procs[:limit])

@app.route("/export/csv")
@login_required
def export_csv():
    return send_file(app.config["CSV_PATH"], as_attachment=True)

@app.route("/report")
@login_required
def report():
    pts = list(history)
    if not pts:
        return jsonify(stats={})
    n = len(pts)
    cpu_vals = [p["cpu"] for p in pts]
    mem_vals = [p["mem"] for p in pts]
    disk_vals = [p["disk"] for p in pts]
    stats = dict(
        count=n,
        cpu_avg=round(sum(cpu_vals)/n, 2), cpu_max=max(cpu_vals),
        mem_avg=round(sum(mem_vals)/n, 2), mem_max=max(mem_vals),
        disk_avg=round(sum(disk_vals)/n, 2), disk_max=max(disk_vals),
    )
    return jsonify(stats=stats)

@app.route("/healthz")
def healthz():
    return "ok", 200

@app.route("/metrics")
def metrics():
    reg = CollectorRegistry()
    g_cpu = Gauge("sys_cpu_percent", "CPU percent", registry=reg)
    g_mem = Gauge("sys_mem_percent", "Memory percent", registry=reg)
    g_disk = Gauge("sys_disk_percent", "Disk percent", registry=reg)
    g_cpu.set(latest.get("cpu", 0))
    g_mem.set(latest.get("mem", 0))
    g_disk.set(latest.get("disk", 0))
    return generate_latest(reg), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)