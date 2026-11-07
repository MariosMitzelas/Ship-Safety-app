from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

CHECKLISTS = {
    "QR123": [
        {"step": "1", "checkpoint": "Check oil level and ensure no leaks are visible."},
        {"step": "2", "checkpoint": "Inspect suction and discharge pressure gauges."},
        {"step": "3", "checkpoint": "Verify cooling water temperature and flow rate."},
        {"step": "4", "checkpoint": "Inspect safety valves and emergency stop switches."}
    ],
    "compressor_room": [
        {"step": "1", "checkpoint": "Inspect cargo compressor seals and barrier space pressure."},
        {"step": "2", "checkpoint": "Verify glycol water circulation and heating system."},
        {"step": "3", "checkpoint": "Check gas detection sampling points and suction lines."},
        {"step": "4", "checkpoint": "Ensure ventilation fan operation and air flow indication."}
    ]
}

SUBMISSIONS_FILE = 'submissions.json'

def load_submissions():
    if os.path.exists(SUBMISSIONS_FILE):
        try:
            with open(SUBMISSIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_submissions(data):
    with open(SUBMISSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def home():
    qr_id = request.args.get('qr_id', 'QR123')
    checklist = CHECKLISTS.get(qr_id, CHECKLISTS["QR123"])
    return render_template('index.html', qr_id=qr_id, checklist=checklist)

@app.route('/submit', methods=['POST'])
@app.route('/submit_checklist', methods=['POST'])
def submit():
    qr_id = request.form.get('qr_id', 'Unknown')
    sailor_name = request.form.get('sailor_name', 'Anonymous')
    shift = request.form.get('shift', 'N/A')
    
    # Διαβάζει τα τσεκαρισμένα checkpoints
    checklist = CHECKLISTS.get(qr_id, CHECKLISTS.get("QR123", []))
    verified_items = []
    
    for item in checklist:
        step_val = item['step']
        # Ελέγχει αν έγινε tick είτε μέσω name="items" είτε μέσω completed_<step>
        if request.form.get(f"completed_{step_val}") == "true" or step_val in request.form.getlist("items"):
            verified_items.append({
                "step": step_val,
                "checkpoint": item['checkpoint'],
                "status": "Verified"
            })
            
    submission = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "qr_id": qr_id,
        "sailor_name": sailor_name,
        "shift": shift,
        "items": verified_items
    }
    
    submissions = load_submissions()
    submissions.insert(0, submission)
    save_submissions(submissions)
    
    return redirect(url_for('view_submissions'))

@app.route('/submissions')
@app.route('/view_submissions')
def view_submissions():
    submissions = load_submissions()
    return render_template('submissions.html', submissions=submissions)

if __name__ == '__main__':
    app.run(debug=True)
