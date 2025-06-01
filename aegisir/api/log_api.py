from flask import Flask, jsonify, send_from_directory, abort, request, Response
import os
from pathlib import Path

app = Flask(__name__)
LOG_ROOT = os.path.abspath("./logs")


@app.route("/logs", methods=["GET"])
def list_logs():
    try:
        logs = sorted(os.listdir(LOG_ROOT), reverse=True)
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logs/latest", methods=["GET"])
def latest_log_folder():
    try:
        logs = sorted(os.listdir(LOG_ROOT), reverse=True)
        return jsonify({"latest": logs[0] if logs else None})
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
    file_path = os.path.join(log_dir, filename)

    if not os.path.isdir(log_dir):
        abort(404, description="Log folder not found")
    if not os.path.exists(file_path):
        abort(404, description="File not found")

    # If ?html=true, show pretty output
    if request.args.get("html") == "true":
        with open(file_path, "r") as f:
            content = f.read()
        return Response(f"<pre>{content}</pre>", mimetype="text/html")

    return send_from_directory(log_dir, filename)


@app.route("/search", methods=["GET"])
def search_logs():
    keyword = request.args.get("q")
    if not keyword:
        return jsonify({"error": "Missing ?q= parameter"}), 400

    results = {}
    for folder in sorted(os.listdir(LOG_ROOT), reverse=True):
        folder_path = os.path.join(LOG_ROOT, folder)
        if not os.path.isdir(folder_path):
            continue
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                matches = [line.strip() for line in lines if keyword.lower() in line.lower()]
                if matches:
                    results[f"{folder}/{file}"] = matches
            except:
                continue

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)

