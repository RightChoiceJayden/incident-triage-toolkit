#!/bin/bash

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_DIR="./logs/$TIMESTAMP"
mkdir -p "$LOG_DIR"

echo "[+] Starting triage at $TIMESTAMP"
echo "[+] Logging to $LOG_DIR"

# Detect OS
OS=$(uname)
echo "[+] Detected OS: $OS"

if [ "$OS" == "Darwin" ]; then
  echo "[+] Detected macOS — using macOS commands"
  top -l 1 > "$LOG_DIR/top.txt"
  ps aux | sort -nrk 3,3 | head -n 15 > "$LOG_DIR/cpu_processes.txt"
  df -h > "$LOG_DIR/disk_usage.txt"
  iostat -w 1 -c 3 > "$LOG_DIR/iostat.txt"
  netstat -an > "$LOG_DIR/network.txt"
else
  echo "[+] Detected Linux — using Linux commands"
  top -b -n1 > "$LOG_DIR/top.txt"
  ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -n 15 > "$LOG_DIR/cpu_processes.txt"
  df -h > "$LOG_DIR/disk_usage.txt"
  iostat -xz 1 3 > "$LOG_DIR/iostat.txt"
  netstat -tulnp > "$LOG_DIR/network.txt"
fi

# Run Python diagnostics
python3 aegisir/triage/collect_stats.py "$LOG_DIR"

# Extract top CPU line and send Slack message
TOP_PROCESS=$(head -n 2 "$LOG_DIR/cpu_processes.txt" | tail -n 1)
python3 aegisir/triage/utils/slack_notifier.py "$TIMESTAMP" "$TOP_PROCESS"

