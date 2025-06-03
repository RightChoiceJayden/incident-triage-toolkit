from flask import Flask, request, jsonify, Response, send_from_directory
from datetime import datetime
import subprocess
import os
import threading
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
from aegisir.triage.utils.slack_notifier import send_slack_message

app = Flask(__name__)
alert_counter = Counter('aegisir_alerts_total', 'Total number of alerts received')

def run_triage():
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = f"./logs/{timestamp}"
    os.makedirs(log_dir, exist_ok=True)

    print(f"[+] Starting triage at {timestamp}")
    print(f"[+] Logging to {log_dir}")

    # Run the shell-based triage script
    shell_cmd = f"./aegisir/triage.sh {log_dir}"
    subprocess.call(shell_cmd, shell=True)

    # Try to extract the top CPU process line
    cpu_summary = None
    cpu_file_path = os.path.join(log_dir, "cpu_processes.txt")

    try:
        with open(cpu_file_path, "r") as f:
            cpu_lines = f.readlines()
            for line in cpu_lines:
                if line.strip() and not line.lower().startswith("user"):  # Skip headers
                    cpu_summary = line.strip()
                    break
    except Exception as e:
        print(f"[!] Failed to read top CPU process: {e}")

    if not cpu_summary:
        cpu_summary = "⚠️ Top CPU process could not be determined."

    # Send Slack message
    try:
        send_slack_message(timestamp, cpu_summary, log_link=None)
    except Exception as e:
        print(f"[!] Slack notification failed: {e}")

@app.route('/alert', methods=['POST'])
def receive_alert():
    alert_counter.inc()
    threading.Thread(target=run_triage).start()
    return jsonify({"status": "triage started"}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/logs/<path:filename>', methods=['GET'])
def get_log_file(filename):
    return send_from_directory('logs', filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

