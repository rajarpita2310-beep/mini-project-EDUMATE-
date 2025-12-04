from flask import Flask, request, jsonify, make_response
from functools import wraps
from datetime import datetime
import uuid
import json

app = Flask(__name__)

# --- Mock Database ---
# Mimics a simple in-memory database structure
MOCK_DB = {
    'users': [
        {'id': 'u1', 'name': 'Prof. Alice', 'email': 'alice@edu.com', 'password': 'pass'}
    ],
    'classes': [
        {'id': 'c1', 'name': '10-A', 'coordinatorName': 'Mr. Smith', 'coordinatorPhone': '555-1001', 'students': [
            {'id': 's1', 'roll': '10A001', 'name': 'Student A', 'email': 'student.a@test.com', 'status': 'Day Scholar', 'phone': '555-0011', 'parentPhone': '555-0021', 'address': '123 Main St', 'previousMarks': 'Math: 80, Science: 90'},
            {'id': 's2', 'roll': '10A002', 'name': 'Student B', 'email': 'student.b@test.com', 'status': 'Hosteller', 'phone': '555-0012', 'parentPhone': '555-0022', 'address': 'Dormitory East', 'previousMarks': 'Math: 75, Science: 85'}
        ]},
        {'id': 'c2', 'name': '11-B', 'coordinatorName': 'Ms. Jones', 'coordinatorPhone': '555-1002', 'students': []}
    ],
    'timetable': [
        {'id': 't1', 'day': 'Monday', 'time': '09:00', 'subject': 'Physics', 'location': 'Lab 1'},
        {'id': 't2', 'day': 'Monday', 'time': '10:00', 'subject': 'Maths', 'location': 'Room 102'},
    ],
    'notifications': [],
    'attendance': [
        {'date': '12/03/2025', 'period': 'Period 1', 'studentId': 's1', 'studentName': 'Student A', 'className': '10-A', 'status': 'P'},
        {'date': '12/03/2025', 'period': 'Period 1', 'studentId': 's2', 'studentName': 'Student B', 'className': '10-A', 'status': 'A'},
    ],
    'exams': [
        {'id': 'e1', 'title': 'Mid-Term Physics', 'totalMarks': 100, 'classId': 'c1'}
    ],
    'scores': [
        {'examId': 'e1', 'studentId': 's1', 'marks': 85},
        {'examId': 'e1', 'studentId': 's2', 'marks': 72}
    ],
    'assignments': [
        {'id': 'a1', 'title': 'Vector Practice', 'className': '10-A', 'date': '12/01/2025', 'category': 'Assignment'},
        {'id': 'a2', 'title': 'Ecology Notes', 'className': '10-A', 'date': '12/02/2025', 'category': 'Study Note'},
    ]
}

# --- Utility Functions ---

def find_student_by_id(student_id):
    """Searches the entire DB for a student by ID."""
    for cls in MOCK_DB['classes']:
        for student in cls['students']:
            if student['id'] == student_id:
                return student, cls
    return None, None

def calculate_attendance(student_id):
    """Calculates attendance for a given student ID."""
    records = [r for r in MOCK_DB['attendance'] if r['studentId'] == student_id]
    total = len(records)
    present = len([r for r in records if r['status'] == 'P'])
    
    percentage = round((present / total) * 100) if total > 0 else 0
    return {'present': present, 'total': total, 'percentage': percentage}

def get_student_scores(student_id):
    """Compiles exam scores for a given student."""
    student_scores = [s for s in MOCK_DB['scores'] if s['studentId'] == student_id]
    exam_results = []
    
    for score in student_scores:
        exam = next((e for e in MOCK_DB['exams'] if e['id'] == score['examId']), None)
        if exam:
            exam_results.append({
                'title': exam['title'],
                'obtained': score['marks'],
                'total': exam['totalMarks']
            })
    return exam_results

# --- API Endpoints ---

## Auth Endpoints
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = next((u for u in MOCK_DB['users'] if u['email'] == email and u['password'] == password), None)
    
    if user:
        # Return user data (excluding password for security)
        return jsonify({'id': user['id'], 'name': user['name'], 'email': user['email']})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'error': 'Missing fields'}), 400
        
    if next((u for u in MOCK_DB['users'] if u['email'] == email), None):
        return jsonify({'error': 'User already exists'}), 409
        
    new_user = {'id': str(uuid.uuid4())[:8], 'name': name, 'email': email, 'password': password}
    MOCK_DB['users'].append(new_user)
    
    return jsonify({'id': new_user['id'], 'name': new_user['name'], 'email': new_user['email']}), 201

## Data Fetch Endpoints (Used by loadAllData)
@app.route('/api/classes', methods=['GET'])
def get_classes():
    # In a real app, you would filter based on the logged-in user.
    return jsonify(MOCK_DB['classes'])

@app.route('/api/timetable', methods=['GET'])
def get_timetable():
    return jsonify(MOCK_DB['timetable'])

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    return jsonify(MOCK_DB['notifications'])

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    return jsonify(MOCK_DB['attendance'])

@app.route('/api/exams', methods=['GET'])
def get_exams():
    return jsonify(MOCK_DB['exams'])

@app.route('/api/assignments', methods=['GET'])
def get_assignments():
    return jsonify(MOCK_DB['assignments'])

## Class List Management
@app.route('/api/classes', methods=['POST'])
def add_class():
    data = request.get_json()
    new_class = {
        'id': str(uuid.uuid4())[:8],
        'name': data.get('name'),
        'coordinatorName': data.get('coordinatorName'),
        'coordinatorPhone': data.get('coordinatorPhone'),
        'students': []
    }
    MOCK_DB['classes'].append(new_class)
    return jsonify(new_class), 201

@app.route('/api/classes/<class_id>', methods=['DELETE'])
def delete_class(class_id):
    global MOCK_DB
    
    # Remove all related exam scores, attendance, etc. in a real app.
    
    original_len = len(MOCK_DB['classes'])
    MOCK_DB['classes'] = [c for c in MOCK_DB['classes'] if c['id'] != class_id]
    
    if len(MOCK_DB['classes']) < original_len:
        return jsonify({'message': 'Class deleted'}), 200
    return jsonify({'error': 'Class not found'}), 404

## Student Management
@app.route('/api/classes/<class_id>/students', methods=['POST'])
def add_student(class_id):
    data = request.get_json()
    cls = next((c for c in MOCK_DB['classes'] if c['id'] == class_id), None)
    
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    
    # Simple check for required fields
    if not all(k in data for k in ('name', 'roll', 'email', 'status')):
        return jsonify({'error': 'Missing student details'}), 400

    new_student = {
        'id': str(uuid.uuid4())[:8],
        'roll': data['roll'],
        'name': data['name'],
        'email': data['email'],
        'status': data['status'],
        'phone': data.get('phone', ''),
        'parentPhone': data.get('parentPhone', ''),
        'address': '',
        'previousMarks': ''
    }
    cls['students'].append(new_student)
    return jsonify(new_student), 201

@app.route('/api/students/<student_id>', methods=['PUT'])
def update_student_profile(student_id):
    data = request.get_json()
    student, cls = find_student_by_id(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Update fields used in openProfile and updateProfile
    if 'address' in data:
        student['address'] = data['address']
    if 'previousMarks' in data:
        student['previousMarks'] = data['previousMarks']
        
    return jsonify({'message': 'Profile updated'}), 200

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    student_to_delete, cls = find_student_by_id(student_id)
    
    if not student_to_delete:
        return jsonify({'error': 'Student not found'}), 404

    # Remove student from the class list
    cls['students'] = [s for s in cls['students'] if s['id'] != student_id]
    
    # In a real app, delete all associated attendance, scores, etc.
    
    return jsonify({'message': 'Student deleted'}), 200

## Timetable Management
@app.route('/api/timetable', methods=['POST'])
def add_timetable_entry():
    data = request.get_json()
    new_entry = {
        'id': str(uuid.uuid4())[:8],
        'day': data.get('day'),
        'time': data.get('time'),
        'subject': data.get('subject'),
        'location': data.get('location')
    }
    MOCK_DB['timetable'].append(new_entry)
    return jsonify(new_entry), 201

@app.route('/api/timetable/<entry_id>', methods=['DELETE'])
def delete_timetable_entry(entry_id):
    global MOCK_DB
    original_len = len(MOCK_DB['timetable'])
    MOCK_DB['timetable'] = [t for t in MOCK_DB['timetable'] if t['id'] != entry_id]
    
    if len(MOCK_DB['timetable']) < original_len:
        return jsonify({'message': 'Timetable entry deleted'}), 200
    return jsonify({'error': 'Entry not found'}), 404

## Notifications
@app.route('/api/notifications', methods=['POST'])
def post_notification():
    data = request.get_json()
    new_notification = {
        'id': str(uuid.uuid4())[:8],
        'message': data.get('message'),
        'className': data.get('className'),
        'timestamp': data.get('timestamp') or datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
    }
    MOCK_DB['notifications'].append(new_notification)
    return jsonify(new_notification), 201

## Attendance
@app.route('/api/attendance', methods=['POST'])
def save_attendance():
    data = request.get_json() # data is expected to be a list of attendance records
    
    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of attendance records'}), 400

    # Add new records to the mock DB. In a real app, you would upsert/check for duplicates.
    MOCK_DB['attendance'].extend(data)
    
    # The frontend expects a JSON response, but doesn't seem to use it.
    return jsonify({'message': f'Saved {len(data)} attendance records'}), 201

## Exams and Scores
@app.route('/api/exams', methods=['POST'])
def create_exam():
    data = request.get_json()
    new_exam = {
        'id': str(uuid.uuid4())[:8],
        'title': data.get('title'),
        'totalMarks': int(data.get('totalMarks', 0)),
        'classId': data.get('classId')
    }
    MOCK_DB['exams'].append(new_exam)
    return jsonify(new_exam), 201

@app.route('/api/exams/<exam_id>', methods=['DELETE'])
def remove_exam(exam_id):
    global MOCK_DB
    original_len = len(MOCK_DB['exams'])
    MOCK_DB['exams'] = [e for e in MOCK_DB['exams'] if e['id'] != exam_id]
    
    if len(MOCK_DB['exams']) < original_len:
        # In a real app, also delete all associated scores
        return jsonify({'message': 'Exam deleted'}), 200
    return jsonify({'error': 'Exam not found'}), 404

@app.route('/api/scores', methods=['GET'])
def get_exam_scores():
    exam_id = request.args.get('examId')
    if not exam_id:
        return jsonify({'error': 'Missing examId'}), 400
        
    scores = [s for s in MOCK_DB['scores'] if s['examId'] == exam_id]
    return jsonify(scores)

@app.route('/api/scores', methods=['POST'])
def save_marks():
    data = request.get_json() # Expected list of {examId, studentId, marks}
    
    # In a real app, you would replace existing scores for the given examId/studentId pair.
    # For this mock, we'll implement simple upsert logic:

    exam_id = data[0]['examId'] if data else None
    
    if not exam_id:
         return jsonify({'error': 'Invalid data format'}), 400
         
    # 1. Remove all old scores for this exam
    global MOCK_DB
    MOCK_DB['scores'] = [s for s in MOCK_DB['scores'] if s['examId'] != exam_id]
    
    # 2. Add new scores
    for item in data:
        try:
            # Ensure marks is an integer
            item['marks'] = int(item['marks'])
        except (ValueError, TypeError):
             item['marks'] = 0 # Default to 0 if invalid
             
        MOCK_DB['scores'].append(item)
        
    return jsonify({'message': 'Marks saved'}), 200

## Material/Assignment Upload
@app.route('/api/upload', methods=['POST'])
def file_upload():
    # In a real application, this would upload the file to a cloud service (e.g., S3, Google Cloud Storage)
    # and return the public URL.
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    # Mock URL
    mock_url = f"http://127.0.0.1:5000/static/uploads/{file.filename.replace(' ', '_')}"
    return jsonify({'url': mock_url}), 200

@app.route('/api/assignments', methods=['POST'])
def save_assignment():
    data = request.get_json()
    new_assignment = {
        'id': str(uuid.uuid4())[:8],
        'title': data.get('title'),
        'className': data.get('className'),
        'date': data.get('date'),
        'category': data.get('category')
    }
    MOCK_DB['assignments'].append(new_assignment)
    return jsonify(new_assignment), 201

## Reports / Analytics
@app.route('/api/students/<student_id>/analytics', methods=['GET'])
def get_student_analytics(student_id):
    student, cls = find_student_by_id(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    attendance_data = calculate_attendance(student_id)
    exam_data = get_student_scores(student_id)

    return jsonify({
        'attendance': attendance_data,
        'exams': exam_data
    })

# --- CORS and Run Configuration ---

@app.after_request
def after_request(response):
    # This is necessary because the JavaScript is using 'http://127.0.0.1:5000'
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*' # Allows requests from any origin
    header['Access-Control-Allow-Headers'] = 'Content-Type'
    header['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # This mock assumes your HTML/JS are served externally, 
    # but handles the base URL request.
    return 'EduMate Flask API Running. Frontend is expected to be served separately (e.g., index.html).'

if __name__ == '__main__':
    # Running on port 5000 to match the API_BASE in the JS: http://127.0.0.1:5000
    print("MOCK API running on http://127.0.0.1:5000")
    print("Use the original HTML/JS frontend to interact with it.")
    app.run(debug=True, port=5000)
