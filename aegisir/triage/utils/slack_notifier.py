import os
import requests
from datetime import datetime

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/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")

def send_slack_message(timestamp, cpu_summary, log_link=None):
    message = f"*🚨 AegisIR Incident Triggered*\n"
    message += f"🕒 Timestamp: `{timestamp}`\n"
    message += f"🔥 Top CPU Process:\n```\n{cpu_summary}```\n"
    if log_link:
        message += f"📎 [View Logs]({log_link})"

    payload = {
        "text": message
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("[Slack] Notification sent.")
    except Exception as e:
        print(f"[Slack] Failed to send: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        send_slack_message(sys.argv[1], sys.argv[2])
    else:
        print("[Slack] Missing arguments")

