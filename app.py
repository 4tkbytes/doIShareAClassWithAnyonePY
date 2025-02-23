from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from typing import List, Tuple
import os
from dotenv import load_dotenv
import os.path

# Load environment variables
load_dotenv()

# Get admin password from environment variable, fallback to None if not set
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD environment variable must be set")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'students.db')

app = Flask(__name__)
CORS(app)  # Enable CORS with SSL support
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

@app.before_request
def before_request():
    if not request.is_secure and not app.debug:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

@app.route('/')
def index():
    return render_template('index.html')

def init_db():
    with app.app_context():
        # Only create if doesn't exist
        if not os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
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

init_db()


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

def get_db() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(DB_PATH)
    return conn, conn.cursor()

@app.route('/add/<name>/<student_id>/<classes>')
def add_student(name: str, student_id: str, classes: str):
    try:
        conn, c = get_db()
        # Replace underscores with spaces in name
        name = name.replace('_', ' ')
        # Insert or update student data
        c.execute('''
            INSERT OR REPLACE INTO students (student_id, full_name, classes)
            VALUES (?, ?, ?)
        ''', (student_id, name, classes))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Student added successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Add these new routes before the if __name__ == '__main__' block

@app.route('/get/student/<identifier>')
def get_student_by_id(identifier: str):
    try:
        conn, c = get_db()
        c.execute('SELECT student_id, full_name, classes FROM students WHERE student_id = ?', (identifier,))
        student = c.fetchone()
        conn.close()
        
        if student:
            return jsonify({
                "status": "success",
                "student_id": student[0],
                "name": student[1],
                "classes": student[2]
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Student not found"
            }), 404
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get/student/name/<name>')
def get_student_by_name(name: str):
    try:
        conn, c = get_db()
        # Replace underscores with spaces in name
        name = name.replace('_', ' ')
        c.execute('SELECT student_id, full_name, classes FROM students WHERE full_name = ?', (name,))
        student = c.fetchone()
        conn.close()
        
        if student:
            return jsonify({
                "status": "success",
                "student_id": student[0],
                "name": student[1],
                "classes": student[2]
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Student not found"
            }), 404
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get/<classes>')
def get_students(classes: str):
    try:
        conn, c = get_db()
        # Split input classes into a set
        input_classes = set(classes.split(','))
        
        # Get all students from database
        c.execute('SELECT student_id, full_name, classes FROM students')
        students = c.fetchall()
        
        # Find student with most matching classes, excluding exact matches
        best_match = None
        max_matches = 0
        
        for student in students:
            student_classes = set(student[2].split(','))
            matches = len(input_classes.intersection(student_classes))
            
            # Skip if all classes match (likely same person)
            if input_classes == student_classes:
                continue
                
            if matches > max_matches:
                max_matches = matches
                best_match = {
                    "name": student[1],
                    "student_id": student[0],
                    "classes": list(student_classes),
                    "matching_classes": list(input_classes.intersection(student_classes))
                }
        
        conn.close()
        
        if best_match:
            return jsonify({
                "status": "success",
                "match": best_match
            })
        else:
            return jsonify({
                "status": "error",
                "message": "No other students with matching classes found"
            }), 404
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Development settings
    if app.debug:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        # Production settings
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, ssl_context='adhoc')