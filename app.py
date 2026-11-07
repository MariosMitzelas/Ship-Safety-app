from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

DATA_FILE = 'safety_checks.csv'

def init_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Sailor_Name', 'Round_ID', 'Status'])

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
``` Αυτός ο βασικός κώδικας δημιουργεί έναν διακομιστή που δέχεται δεδομένα και τα αποθηκεύει σε αρχείο.
