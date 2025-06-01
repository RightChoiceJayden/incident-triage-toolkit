#!/bin/bash

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_DIR="/var/log/aegisir/$TIMESTAMP"
mkdir -p "$LOG_DIR"

echo "[+] Starting triage at $TIMESTAMP"
echo "[+] Logging to $LOG_DIR"

top -b -n1 > "$LOG_DIR/top.txt"
ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -n 15 > "$LOG_DIR/cpu_processes.txt"
df -h > "$LOG_DIR/disk_usage.txt"
iostat -xz 1 3 > "$LOG_DIR/iostat.txt"
netstat -tulnp > "$LOG_DIR/network.txt"

python3 aegisir/triage/collect_stats.py "$LOG_DIR"

