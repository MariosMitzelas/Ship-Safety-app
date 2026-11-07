from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

DATA_FILE = 'safety_checks.csv'
CHECKLISTS_FILE = 'checklists_template.csv'

def init_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Sailor_Name', 'Round_ID', 'Status'])

def load_checklists():
    checklists = {}
    if os.path.exists(CHECKLISTS_FILE):
        with open(CHECKLISTS_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                qr_id = row['QR_ID']
                if qr_id not in checklists:
                    checklists[qr_id] = []
                checklists[qr_id].append({
                    'step_number': row['Step_Number'],
                    'checkpoint': row['Checkpoint']
                })
    return checklists

@app.route('/get_checklist', methods=['GET'])
def get_checklist():
    qr_id = request.args.get('qr_id')
    checklists = load_checklists()
    if qr_id in checklists:
        return jsonify({'qr_id': qr_id, 'checklist': checklists[qr_id]}), 200
    return jsonify({'error': 'Checklist not found'}), 404

@app.route('/submit', methods=['POST'])
def submit_check():
    data = request.form
    timestamp = data.get('timestamp')
    sailor_name = data.get('sailor_name')
    round_id = data.get('round_id')
    status = data.get('status')
    
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, sailor_name, round_id, status])
        
    return jsonify({'message': 'Success'}), 200

if __name__ == '__main__':
    init_csv()
    app.run(host='0.0.0.0', port=5000)
``` Αυτός ο κώδικας διαβάζει το αρχείο με τις λίστες και επιστρέφει τα βήματα ανάλογα με τον κωδικό QR που θα σκαναριστεί.
