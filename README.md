# 🚀 System Monitoring & Automation Toolkit (Python + Flask + psutil)

A real-time **system monitoring dashboard** that tracks CPU, Memory, Disk, and Network stats — built with **Python, Flask, psutil, threads, Prometheus metrics, secure auth**, and **auto-refresh front-end**.

> Built to simulate IT automation / DevOps monitoring systems like Datadog, Nagios, and Grafana dashboards.

---

## ✨ Features

✅ Secure login (hashed password via Werkzeug)
✅ Live CPU, RAM, Disk, & alert bar view
✅ Auto-refresh dashboard every **3 seconds**
✅ Background system sampler thread
✅ CSV logging + rotation
✅ Plot-ready historical exports
✅ Top processes API (like `htop`)
✅ Prometheus `/metrics` endpoint
✅ System health alerts (OK / Warning / Critical)
✅ Easy deploy with Docker

---

## 📸 Live UI Screenshots (with Auto-Refresh)

### **Login Screen**

| Sign-in Page                                            |
| ------------------------------------------------------- |
|<img width="537" height="400" alt="image" src="https://github.com/user-attachments/assets/b923527b-4096-4c43-b0a9-2d93555c0786" />|

---

### **Real-Time Monitoring Dashboard**

| CPU Load-I                                                                                           |
| ---------------------------------------------------------------------------------------------------- |
|<img width="490" height="419" alt="image" src="https://github.com/user-attachments/assets/e9b7c1df-a3cb-415d-a121-59cdd54e6374" />|

| CPU Load-II                                                                                          |
|------------------------------------------------------------------------------------------------------|
|<img width="438" height="379" alt="image" src="https://github.com/user-attachments/assets/7cafede6-e07a-44f8-8fa5-7a172e4e2e09" />|

| CPU Load-III                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------- |
| <img width="461" height="411" alt="image" src="https://github.com/user-attachments/assets/a61320a1-6b42-438e-859a-17be58ffc919" />|

| Auto-Refreshing Every 3 Seconds                                      |
|----------------------------------------------------------------------|
| System updates continuously with fresh stats (no page reload needed) |

🕒 **Auto-Refresh Interval:** every **3 seconds** (asynchronous fetch from `/data`)
🎯 *Mimics professional live monitoring dashboards*

---

## 🧠 Architecture

```
Browser UI (JS fetch every 3s)
        ↓
Flask App ──> Auth ──> Dashboard
        ↓
Background Thread (Sampler)
        ↓
psutil → live metrics → memory + CSV
        ↓
/data        → front-end updates
/top         → processes like htop
/metrics     → Prometheus scrape
/export/csv  → download logs
```

---

## 🏗️ Tech Stack

| Layer          | Tech                                     |
| -------------- | ---------------------------------------- |
| Backend        | Python, Flask                            |
| System Metrics | psutil                                   |
| Security       | Werkzeug hashing, secure session cookies |
| Frontend       | HTML, CSS, JavaScript                    |
| Observability  | Prometheus client                        |
| Logging        | CSV with rotation                        |
| Deployment     | Docker                                   |

---

## 📂 Folder Structure

```
📦 system-monitoring-tool
 ┣ 📁 static
 ┃ ┣ 📁 css
 ┃ ┣ 📁 js
 ┃ ┗ 📁 Screenshots       
 ┣ 📁 templates
 ┃ ┣ index.html
 ┃ ┗ login.html
 ┣ 📁 data            # CSV logs here
 ┣ app.py
 ┣ config.py
 ┣ requirements.txt
 ┣ Dockerfile
 ┗ README.md
```

---

## ⚙️ Installation

### 1) Clone Repo

```bash
git clone - https://github.com/shreyakri803/System-Monitoring-Automation-Toolkit.git
cd system-monitor
```

### 2) Create Virtual Env

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .\.venv\Scripts\activate
```

### 3) Install Requirements

```bash
pip install -r requirements.txt
```

### 4) Run App

```bash
python app.py
```

Visit → `http://127.0.0.1:5000`

Default user (if not using `.env`):

```
username: admin
password: admin123
```

---

## 🔥 API Endpoints

| Endpoint      | Description                   |
| ------------- | ----------------------------- |
| `/`           | Live dashboard                |
| `/data`       | Real-time JSON metrics        |
| `/top`        | Top CPU processes (like htop) |
| `/history`    | Pull past metrics             |
| `/report`     | Stats summary                 |
| `/export/csv` | Download logs                 |
| `/metrics`    | Prometheus endpoint           |
| `/login`      | Auth                          |
| `/logout`     | End session                   |

---

## 🧪 Sample `/data` Output

```json
{
  "cpu": 17.3,
  "mem": 62.8,
  "disk": 49.2,
  "net": {
    "bytes_sent": 9320815,
    "bytes_recv": 21933824
  },
  "status": "OK"
}
```

---

## 🚧 Future Enhancements

* Slack/Email alerts for spikes
* Chart.js based graph dashboard
* Windows service / Linux systemd unit
* Grafana panel export
* CPU temp + GPU support

---

## 👤 Author

**Shreya Kumari**
📎 LinkedIn: *linkedin.com/in/shreya-k-986a8321b*
