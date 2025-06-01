from flask import Flask, jsonify, send_from_directory, abort
import os

app = Flask(__name__)
LOG_ROOT = os.path.abspath("./logs")


@app.route("/logs", methods=["GET"])
def list_logs():
    try:
        logs = sorted(os.listdir(LOG_ROOT), reverse=True)
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logs/<timestamp>", methods=["GET"])
def list_files_in_log(timestamp):
    log_dir = os.path.join(LOG_ROOT, timestamp)
    if not os.path.isdir(log_dir):
        abort(404, description="Log folder not found")
    return jsonify(os.listdir(log_dir))


@app.route("/logs/<timestamp>/<filename>", methods=["GET"])
def get_log_file(timestamp, filename):
    log_dir = os.path.join(LOG_ROOT, timestamp)
    if not os.path.isdir(log_dir):
        abort(404, description="Log folder not found")
    if not os.path.exists(os.path.join(log_dir, filename)):
        abort(404, description="File not found")
    return send_from_directory(log_dir, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)

