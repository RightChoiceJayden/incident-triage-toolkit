#!/bin/bash

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_DIR="./logs/$TIMESTAMP"
mkdir -p "$LOG_DIR"

echo "[+] Starting triage at $TIMESTAMP"
echo "[+] Logging to $LOG_DIR"

OS=$(uname)
if [[ "$OS" == "Darwin" ]]; then
    echo "[+] Detected macOS — using macOS commands"
    OS="macos"
else
    echo "[+] Detected Linux — using Linux commands"
    OS="linux"
fi

# Capture top output
if [[ "$OS" == "macos" ]]; then
    echo "[+] Capturing top output (macOS)"
    top -l 1 -n 5 -s 0 > "$LOG_DIR/top.txt"
else
    echo "[+] Capturing top output (Linux)"
    top -b -n 1 > "$LOG_DIR/top.txt"
fi

# Capture CPU-heavy processes
echo "[+] Capturing CPU-heavy processes"
ps aux | sort -nrk 3,3 | head -n 10 > "$LOG_DIR/cpu_processes.txt"

# Capture disk usage
echo "[+] Capturing disk usage"
df -h > "$LOG_DIR/disk_usage.txt"

# Capture I/O stats
if [[ "$OS" == "macos" ]]; then
    echo "[+] Capturing I/O stats (macOS)"
    iostat -Id -w 1 -c 2 > "$LOG_DIR/iostat.txt"
else
    echo "[+] Capturing I/O stats (Linux)"
    iostat -x 1 2 > "$LOG_DIR/iostat.txt"
fi

# Capture network info
if [[ "$OS" == "macos" ]]; then
    echo "[+] Capturing network stats (macOS)"
    netstat -ib > "$LOG_DIR/network.txt"
else
    echo "[+] Capturing network stats (Linux)"
    netstat -tulnp > "$LOG_DIR/network.txt"
fi

# Trigger Python-based triage
echo "[+] Python triage started at $(date)"
python3 aegisir/triage/collect_stats.py "$LOG_DIR"
echo "[+] Python triage complete. Logs stored in $LOG_DIR"

