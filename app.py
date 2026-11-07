import csv
from flask import Flask, jsonify, request

app = Flask(__name__)


def load_checklists():
  checklists = {}
  try:
    with open("checklists_template.csv", mode="r", encoding="utf-8") as f:
      reader = csv.DictReader(f)
      for row in reader:
        qr = row.get("QR_ID", "").strip()
        step = row.get("Step_Number", "").strip()
        checkpoint = row.get("Checkpoint", "").strip()
        if qr:
          if qr not in checklists:
            checklists[qr] = []
          checklists[qr].append({"step": step, "checkpoint": checkpoint})
  except Exception as e:
    print(f"Error reading CSV: {e}")
  return checklists


@app.route("/")
def home():
  return "Checklist API is running!"


@app.route("/get_checklist", methods=["GET"])
def get_checklist():
  qr_id = request.args.get("qr_id", "").strip()
  if not qr_id:
    return jsonify({"error": "Missing qr_id parameter"}), 400

  data = load_checklists()
  if qr_id in data:
    return jsonify({"qr_id": qr_id, "checklist": data[qr_id]})
  else:
    return jsonify({"error": "Checklist not found"}), 404


if __name__ == "__main__":
  app.run()
