async function fetchJSON(url) {
  const r = await fetch(url, { cache: "no-store" });
  if (!r.ok) throw new Error(url + " -> " + r.status);
  return r.json();
}

function setPct(idText, idBar, v) {
  const val = document.getElementById(idText);
  const bar = document.getElementById(idBar);
  val.textContent = `${v.toFixed(0)}%`;
  bar.style.width = `${Math.max(0, Math.min(100, v))}%`;
}

function setStatus(status) {
  const s = document.getElementById("status");
  const bar = document.getElementById("alert-bar");
  s.textContent = status;
  bar.classList.remove("ok","warn","crit");
  if (status === "Critical") bar.classList.add("crit");
  else if (status === "Warning") bar.classList.add("warn");
  else bar.classList.add("ok");
  bar.style.width = status === "OK" ? "100%" : status === "Warning" ? "66%" : "33%";
}

async function refresh() {
  try {
    const d = await fetchJSON("/data");
    if (d.status === "WarmingUp") {
      console.log("Sampler warming up…");
      return;
    }
    setPct("cpu-val", "cpu-bar", d.cpu || 0);
    setPct("mem-val", "mem-bar", d.mem || 0);
    setStatus(d.status || "OK");
  } catch (e) {
    console.error("Refresh error:", e);
    setStatus("Critical");
  }
}

function countdown(sec) {
  let left = sec;
  const el = document.getElementById("next");
  el.textContent = `Next update in ${left}s`;
  const t = setInterval(() => {
    left -= 1;
    if (left <= 0) { clearInterval(t); el.textContent = `Next update in ${sec}s`; }
    else { el.textContent = `Next update in ${left}s`; }
  }, 1000);
}

(async function boot() {
  await refresh();
  setInterval(() => { refresh(); countdown(3); }, 3000);
})();
