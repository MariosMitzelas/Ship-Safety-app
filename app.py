import os
from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATA_FILE = 'submissions.json'

def load_submissions():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_submissions(submissions):
    with open(DATA_FILE, 'w') as f:
        json.dump(submissions, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    sailor_name = request.form.get('sailor_name')
    shift = request.form.get('shift')
    items = request.form.getlist('items')
    
    uploaded_files = request.files.getlist('qr_image')
    file_paths = []
    for file in uploaded_files:
        if file and file.filename:
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            file_paths.append(filepath)

    submission_data = {
        'sailor_name': sailor_name,
        'shift': shift,
        'items': items,
        'qr_images': file_paths,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    submissions = load_submissions()
    submissions.append(submission_data)
    save_submissions(submissions)

    return redirect(url_for('submissions'))

@app.route('/submissions')
def submissions():
    submissions_data = load_submissions()
    return render_template('submissions.html', submissions=submissions_data)

if __name__ == '__main__':
    app.run(debug=True)
