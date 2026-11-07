import datetime
import json
import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

CHECKLISTS = {
    "QR123": {
        "qr_id": "QR123",
        "title": "Equipment Safety Check",
        "checklist": [
            {
                "step": 1,
                "checkpoint": "Check fluid levels and inspect for leaks",
            },
            {
                "step": 2,
                "checkpoint": "Test brake functionality and linkage tension",
            },
            {
                "step": 3,
                "checkpoint": "Verify emergency stop operation",
            },
        ],
    }
}

SUBMISSIONS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "submissions.json"
)


def cleanup_old_submissions():
  if not os.path.exists(SUBMISSIONS_FILE):
    return

  try:
    with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
      data = json.load(f)
      if not isinstance(data, list):
        return
  except (json.JSONDecodeError, Exception):
    return

  cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)
  fresh_data = []

  for entry in data:
    try:
      entry_date = datetime.datetime.strptime(entry["date"], "%Y-%m-%d")
      if entry_date >= cutoff_date:
        fresh_data.append(entry)
    except (ValueError, KeyError):
      continue

  if len(fresh_data) != len(data):
    with open(SUBMISSIONS_FILE, "w", encoding="utf-8") as f:
      json.dump(fresh_data, f, indent=4, ensure_ascii=False)


@app.route("/")
def home():
  return render_template("index.html")


@app.route("/get_checklist", methods=["GET"])
def get_checklist():
  qr_id = request.args.get("qr_id", "").strip()
  if not qr_id:
    return jsonify({"error": "Missing qr_id parameter"}), 400

  data = CHECKLISTS.get(qr_id)
  if not data:
    return jsonify({"error": f"Checklist not found for ID: {qr_id}"}), 404

  return jsonify(data), 200


@app.route("/submit_checklist", methods=["POST"])
def submit_checklist():
  payload = request.get_json(silent=True)
  if not payload:
    return (
        jsonify({"success": False, "error": "Invalid or missing JSON payload"}),
        400,
    )

  qr_id = payload.get("qr_id")
  sailor_name = payload.get("sailor_name")
  shift = payload.get("shift")
  items = payload.get("items")

  if not qr_id or not sailor_name or not shift or not isinstance(items, list):
    return (
        jsonify(
            {
                "success": False,
                "error": (
                    "Missing required fields: qr_id, sailor_name, shift, or"
                    " items"
                ),
            }
        ),
        422,
    )

  now = datetime.datetime.utcnow()
  submission_entry = {
      "submission_id": f"{qr_id}_{int(now.timestamp())}",
      "qr_id": qr_id,
      "sailor_name": sailor_name,
      "date": now.strftime("%Y-%m-%d"),
      "time_utc": now.strftime("%H:%M:%S"),
      "shift": shift,
      "items": items,
  }

  try:
    data = []
    if os.path.exists(SUBMISSIONS_FILE):
      with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
        try:
          data = json.load(f)
          if not isinstance(data, list):
            data = []
        except json.JSONDecodeError:
          data = []

    data.append(submission_entry)

    with open(SUBMISSIONS_FILE, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=4, ensure_ascii=False)

    cleanup_old_submissions()

    return (
        jsonify({
            "success": True,
            "message": "Checklist submitted successfully",
            "submission": submission_entry,
        }),
        201,
    )

  except Exception as e:
    return jsonify({"success": False, "error": f"File storage failure: {e}"}), 500


@app.route("/view_submissions", methods=["GET"])
def view_submissions():
  data = []
  if os.path.exists(SUBMISSIONS_FILE):
    try:
      with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, list):
          data = []
    except (json.JSONDecodeError, Exception):
      data = []

  data.sort(
      key=lambda x: x.get("time_utc", ""),
      reverse=True,
  )
  return render_template("submissions.html", submissions=data)


if __name__ == "__main__":
  app.run(debug=True)
