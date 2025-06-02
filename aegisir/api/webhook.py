from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/alert', methods=['POST'])
def handle_alert():
    try:
        subprocess.Popen(["./aegisir/triage.sh"])
        return "Triage triggered", 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

