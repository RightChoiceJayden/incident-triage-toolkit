# AegisIR: Realtime Incident Response Toolkit

AegisIR is a minimal, production-aware incident response toolkit that combines real-time alerting, lightweight system triage, and Slack notifications. Built for modern engineering teams who want just enough observability to detect, respond to, and log performance-impacting issues — with zero fluff and maximum clarity.

---

## 🚀 What It Does

* **Listens for alerts** from Prometheus or external monitoring tools
* **Runs system-level triage** scripts capturing CPU, disk, memory, network metrics
* **Captures logs in structured, timestamped directories** for easy auditing
* **Sends formatted Slack notifications** with real-time process data
* **Exposes Prometheus-compatible metrics** at `/metrics` for observability

---

## 🔧 How It Works (Detailed Walkthrough)

### 1. Prometheus Monitors CPU

Using node\_exporter, Prometheus collects host metrics. We define an alert when CPU usage exceeds 85%:

```yaml
- alert: HighCPUUsage
  expr: 100 - (avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[2m])) * 100) > 85
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "High CPU usage detected on {{ $labels.instance }}"
```

### 2. Alertmanager Triggers AegisIR

This alert is routed via Alertmanager to AegisIR’s Flask API:

```yaml
receivers:
  - name: 'aegisir'
    webhook_configs:
      - url: 'http://aegisir:5001/alert'
```

### 3. Flask Webhook Executes Shell Triage

Inside `webhook.py`, the `/alert` endpoint starts `run_triage()` in a background thread:

```python
@app.route('/alert', methods=['POST'])
def receive_alert():
    alert_counter.inc()
    threading.Thread(target=run_triage).start()
    return jsonify({"status": "triage started"}), 200
```

This function creates a timestamped directory, runs `triage.sh`, and extracts the top CPU-consuming process from the logs.

### 4. `triage.sh` Logs System Stats

This Bash script dynamically detects whether it's running on macOS or Linux and runs different sets of commands accordingly:

```bash
OS=$(uname)
if [[ "$OS" == "Darwin" ]]; then
    echo "[+] Detected macOS — using macOS commands"
    top -l 1 -n 5 -s 0 > "$LOG_DIR/top.txt"
    iostat -Id -w 1 -c 2 > "$LOG_DIR/iostat.txt"
    netstat -ib > "$LOG_DIR/network.txt"
else
    echo "[+] Detected Linux — using Linux commands"
    top -b -n 1 > "$LOG_DIR/top.txt"
    iostat -x 1 2 > "$LOG_DIR/iostat.txt"
    netstat -tulnp > "$LOG_DIR/network.txt"
fi
ps aux | sort -nrk 3,3 | head -n 10 > "$LOG_DIR/cpu_processes.txt"
df -h > "$LOG_DIR/disk_usage.txt"
```

### 5. Flask Parses Results

After triage, the Flask backend parses `cpu_processes.txt` to extract a clean CPU summary:

```python
cpu_file_path = os.path.join(log_dir, "cpu_processes.txt")
cpu_summary = None
try:
    with open(cpu_file_path, "r") as f:
        for line in f:
            if line.strip() and not line.lower().startswith("user"):
                cpu_summary = line.strip()
                break
except Exception as e:
    cpu_summary = "⚠️ Top CPU process could not be determined."
```

### 6. Slack Notification

The `send_slack_message()` function formats and sends the notification:

````python
message = f"*🚨 AegisIR Incident Triggered*\n🕒 Timestamp: `{timestamp}`\n🔥 Top CPU Process:\n```\n{cpu_summary}```"
payload = {"text": message}
requests.post(SLACK_WEBHOOK_URL, json=payload)
````

---

## 📸 Example Slack Message

```
*🚨 AegisIR Incident Triggered*
🕒 Timestamp: `2025-06-02_18-33-31`
🔥 Top CPU Process:
```

user   24842   3.9  0.4 ... /Slack Helper (GPU)

```
```

---

## 📂 File Structure

```
incident-triage-toolkit/
├── aegisir/
│   ├── api/
│   │   └── webhook.py           # Flask app receiving alerts and handling triage
│   ├── triage/
│   │   ├── triage.sh            # Shell-based system triage script (OS-aware)
│   │   ├── utils/
│   │   │   └── slack_notifier.py # Slack message formatter and sender
├── logs/                        # Timestamped log directories
├── docker-compose.yml          # Multi-service orchestration
├── Dockerfile                  # Flask app container setup
├── .env                        # SLACK_WEBHOOK_URL and config vars
├── requirements.txt            # Python dependencies
```

---

## ⚙️ Setup & Run

### 1. Clone & Configure

```bash
git clone https://github.com/your-username/incident-triage-toolkit.git
cd incident-triage-toolkit
echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/..." > .env
```

### 2. Launch the Stack

```bash
docker-compose up --build
```

### 3. Test It

```bash
curl -X POST http://localhost:5001/alert
```

---

## 📊 Monitoring Stack

* **Prometheus** scrapes metrics from AegisIR, node\_exporter, and itself
* **Alertmanager** triggers based on rules in `alert_rules.yml`
* **Node Exporter** exposes raw Linux/macOS metrics (CPU, memory, etc.)

---

## ✅ Current Features

* [x] Slack-based alerting
* [x] Triage shell scripts (OS-aware)
* [x] Timestamped log directories
* [x] Prometheus-compatible metrics endpoint
* [x] Healthcheck-ready Docker setup

---

## 🌱 Roadmap

* [ ] Downloadable log viewer UI
* [ ] Dashboard integration with Grafana
* [ ] Container-aware triage enhancements

---

## 👤 Author

**Jayden Harris** — [LinkedIn](https://linkedin.com/in/rightchoicejayden) | [GitHub](https://github.com/rightchoicejayden)

---


