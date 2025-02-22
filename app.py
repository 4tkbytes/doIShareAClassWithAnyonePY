from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests
from requests.exceptions import Timeout, RequestException
import os
import sqlite3
from typing import List, Tuple

ADMIN_PASSWORD = "password123"

app = Flask(__name__)
CORS(app)  # Enable CORS

# Determine environment and set appropriate BASE_URL
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'
BASE_URL = (
    "https://do-i-share-a-class-with-anyone-7a9e11f397f2.herokuapp.com" 
    if IS_PRODUCTION 
    else "http://localhost:5000"
)
TIMEOUT_SECONDS = 25

print(f"Running in {'production' if IS_PRODUCTION else 'development'} mode")
print(f"Using BASE_URL: {BASE_URL}")

def make_request(endpoint: str) -> tuple:
    try:
        response = requests.get(
            f"{BASE_URL}/{endpoint}", 
            timeout=TIMEOUT_SECONDS
        )
        return jsonify(response.json()), 200
    except Timeout:
        return jsonify({
            "status": "error",
            "message": "Request timed out. Please try again."
        }), 504
    except RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"API request failed: {str(e)}"
        }), 500

@app.route('/')
def index():
    return render_template('index.html')

# Database initialization
def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            classes TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Add these new routes before the if __name__ == '__main__' block
@app.route('/clear/<password>')
def clear_database(password: str):
    if password != ADMIN_PASSWORD:
        return jsonify({"status": "error", "message": "Invalid password"}), 403
    
    try:
        conn, c = get_db()
        c.execute('DELETE FROM students')
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Database cleared successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/clear/<password>/<identifier>')
def clear_student(password: str, identifier: str):
    if password != ADMIN_PASSWORD:
        return jsonify({"status": "error", "message": "Invalid password"}), 403
    
    try:
        conn, c = get_db()
        # Try to delete by student ID first, then by name if no rows were affected
        c.execute('DELETE FROM students WHERE student_id = ?', (identifier,))
        if c.rowcount == 0:
            # If no rows were deleted, try matching by name (replacing underscores with spaces)
            name = identifier.replace('_', ' ')
            c.execute('DELETE FROM students WHERE full_name = ?', (name,))
        
        affected_rows = c.rowcount
        conn.commit()
        conn.close()
        
        if affected_rows > 0:
            return jsonify({
                "status": "success", 
                "message": f"Deleted {affected_rows} student(s)"
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "No matching student found"
            }), 404
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Helper function to connect to database
def get_db() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect('students.db')
    return conn, conn.cursor()

@app.route('/add/<name>/<student_id>/<classes>')
def add_student(name: str, student_id: str, classes: str):
    return make_request(f"add/{name}/{student_id}/{classes}")

@app.route('/get/student/<identifier>')
def get_student_by_id(identifier: str):
    return make_request(f"get/student/{identifier}")

@app.route('/get/student/name/<name>')
def get_student_by_name(name: str):
    return make_request(f"get/student/name/{name}")

@app.route('/get/<classes>')
def get_students(classes: str):
    return make_request(f"get/{classes}")

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)