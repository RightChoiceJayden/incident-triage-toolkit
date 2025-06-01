import os
import sys
import subprocess
from datetime import datetime

log_dir = sys.argv[1] if len(sys.argv) > 1 else "."

def run_cmd(cmd, output_file):
    with open(os.path.join(log_dir, output_file), "w") as f:
        f.write(f"$ {cmd}\\n")
        f.write(subprocess.getoutput(cmd))

print(f"[+] Python triage started at {datetime.now()}")

run_cmd("docker ps", "docker_containers.txt")
run_cmd("docker stats --no-stream", "docker_stats.txt")
run_cmd("lsof -nP | head -n 100", "open_files.txt")

print(f"[+] Python triage complete. Logs stored in {log_dir}")

