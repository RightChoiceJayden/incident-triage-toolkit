import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get webhook from environment
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_message(timestamp, cpu_summary, log_link=None):
    if not SLACK_WEBHOOK_URL:
        print("[Slack] Webhook URL not set.")
        return

    message = f"*🚨 AegisIR Incident Triggered*\n"
    message += f"🕒 Timestamp: `{timestamp}`\n"
    message += f"🔥 Top CPU Process:\n```\n{cpu_summary}```\n"
    if log_link:
        message += f"📎 [View Logs]({log_link})"

    payload = {"text": message}

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("[Slack] Notification sent.")
    except Exception as e:
        print(f"[Slack] Failed to send: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        timestamp = sys.argv[1]
        cpu_summary = sys.argv[2]
        log_link = sys.argv[3] if len(sys.argv) > 3 else None
        send_slack_message(timestamp, cpu_summary, log_link)
    else:
        print("[Slack] Missing arguments")

