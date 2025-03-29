from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import csv
import os

app = Flask(__name__)
app.secret_key = "secret_key"

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Nirmal@123",
    "database": "energy_data"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM energy_production ORDER BY date DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', energy_data=data)

@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        import_csv_to_db(filepath)
        flash('CSV file uploaded successfully!')
    else:
        flash('Invalid file format! Please upload a CSV.')
    
    return redirect(url_for('index'))

def import_csv_to_db(filepath):
    conn = get_db_connection()
    cursor = conn.cursor()
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # Skip header
        for row in csv_reader:
            cursor.execute("""
                INSERT INTO energy_production (source, location, date, energy_kwh)
                VALUES (%s, %s, %s, %s)
            """, row)
    conn.commit()
    cursor.close()
    conn.close()
    os.remove(filepath)  # Clean up uploaded file

if __name__ == '__main__':
    app.run(debug=True)