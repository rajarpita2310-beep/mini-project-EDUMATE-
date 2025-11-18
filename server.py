import os
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import db, Class, Student, Teacher, Timetable, Notification, Attendance, Exam, Score

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'edumate.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- AUTHENTICATION ---
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    if Teacher.query.filter_by(email=data['email']).first(): 
        return jsonify({'error': 'Email already registered'}), 400
    
    new_teacher = Teacher(
        id="t"+str(uuid.uuid4())[:8], 
        name=data['name'], 
        email=data['email'], 
        password=data['password']
    )
    db.session.add(new_teacher)
    db.session.commit()
    return jsonify(new_teacher.to_dict()), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    teacher = Teacher.query.filter_by(email=data['email']).first()
    if teacher and teacher.password == data['password']: 
        return jsonify(teacher.to_dict())
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/teacher/<id>/notepad', methods=['PUT'])
def update_notepad(id):
    teacher = Teacher.query.get(id)
    if teacher:
        teacher.notepad = request.json.get('notepad', '')
        db.session.commit()
        return jsonify({'msg': 'Saved'})
    return jsonify({'error': 'Not found'}), 404

# --- CLASS MANAGEMENT (Fixed) ---
@app.route('/api/classes', methods=['GET'])
def get_classes():
    classes = Class.query.all()
    return jsonify([c.to_dict() for c in classes])

@app.route('/api/classes', methods=['POST'])
def create_class():
    data = request.json
    new_class = Class(
        id="c"+str(uuid.uuid4())[:8], 
        name=data['name'], 
        coordinator_name=data['coordinatorName'], 
        coordinator_phone=data['coordinatorPhone']
    )
    db.session.add(new_class)
    db.session.commit()
    return jsonify(new_class.to_dict()), 201

@app.route('/api/classes/<class_id>', methods=['DELETE'])
def delete_class(class_id):
    cls = Class.query.get(class_id)
    if cls: 
        db.session.delete(cls)
        db.session.commit()
        return jsonify({'msg': 'Deleted'})
    return jsonify({'error': 'Not found'}), 404

# --- STUDENT MANAGEMENT ---
@app.route('/api/classes/<class_id>/students', methods=['POST'])
def add_student(class_id):
    data = request.json
    new_student = Student(
        id="s"+str(uuid.uuid4())[:8], 
        name=data['name'], 
        roll=data['roll'], 
        class_id=class_id
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.to_dict()), 201

@app.route('/api/students/<student_id>', methods=['PUT', 'DELETE'])
def handle_student(student_id):
    s = Student.query.get(student_id)
    if not s: return jsonify({'error': 'Not found'}), 404
    
    if request.method == 'DELETE': 
        db.session.delete(s)
        db.session.commit()
        return jsonify({'msg': 'Deleted'})
    
    # UPDATE logic
    data = request.json
    if 'status' in data: s.status = data['status']
    if 'phone' in data: s.phone = data['phone']
    if 'email' in data: s.email = data['email']
    if 'parentPhone' in data: s.parent_phone = data['parentPhone']
    if 'parentEmail' in data: s.parent_email = data['parentEmail']
    db.session.commit()
    return jsonify(s.to_dict())

@app.route('/api/students/<student_id>/analytics', methods=['GET'])
def get_student_analytics(student_id):
    attendance_records = Attendance.query.filter_by(student_id=student_id).all()
    total = len(attendance_records)
    present = len([r for r in attendance_records if r.status == 'P'])
    percentage = round((present / total * 100), 1) if total > 0 else 0

    scores = Score.query.filter_by(student_id=student_id).all()
    score_data = []
    for sc in scores:
        exam = Exam.query.get(sc.exam_id)
        if exam:
            score_data.append({'exam': exam.title, 'total': exam.total_marks, 'obtained': sc.marks_obtained})

    return jsonify({'attendance': {'percentage': percentage, 'present': present, 'total': total}, 'scores': score_data})

# --- EXAMS & SCORES ---
@app.route('/api/exams', methods=['GET', 'POST'])
def handle_exams():
    if request.method == 'GET': return jsonify([e.to_dict() for e in Exam.query.all()])
    data = request.json
    db.session.add(Exam(id="e"+str(uuid.uuid4())[:8], title=data['title'], total_marks=data['totalMarks']))
    db.session.commit()
    return jsonify({'msg': 'Created'}), 201

@app.route('/api/exams/<exam_id>', methods=['DELETE'])
def delete_exam(exam_id):
    e = Exam.query.get(exam_id)
    if e: 
        Score.query.filter_by(exam_id=exam_id).delete()
        db.session.delete(e)
        db.session.commit()
        return jsonify({'msg': 'Deleted'})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/scores', methods=['POST', 'GET'])
def handle_scores():
    if request.method == 'POST':
        for rec in request.json:
            existing = Score.query.filter_by(exam_id=rec['examId'], student_id=rec['studentId']).first()
            if existing: existing.marks_obtained = rec['marks']
            else: db.session.add(Score(exam_id=rec['examId'], student_id=rec['studentId'], marks_obtained=rec['marks']))
        db.session.commit()
        return jsonify({'msg': 'Saved'}), 201
    
    eid = request.args.get('examId')
    if eid: return jsonify([s.to_dict() for s in Score.query.filter_by(exam_id=eid).all()])
    return jsonify([])

# --- TIMETABLE & NOTIFICATIONS & ATTENDANCE ---
@app.route('/api/timetable', methods=['GET', 'POST'])
def handle_timetable():
    if request.method == 'GET': return jsonify([t.to_dict() for t in Timetable.query.all()])
    db.session.add(Timetable(id="tt"+str(uuid.uuid4())[:8], **request.json))
    db.session.commit()
    return jsonify({'msg': 'Added'}), 201

@app.route('/api/timetable/<id>', methods=['DELETE'])
def delete_timetable(id):
    t=Timetable.query.get(id)
    if t: db.session.delete(t); db.session.commit(); return jsonify({'msg':'Deleted'})
    return jsonify({'error':'Not found'}), 404

@app.route('/api/notifications', methods=['GET', 'POST'])
def handle_notifications():
    if request.method == 'GET': return jsonify([n.to_dict() for n in Notification.query.all()])
    data=request.json
    db.session.add(Notification(id="n"+str(uuid.uuid4())[:8], message=data['message'], class_name=data['className'], timestamp=data['timestamp']))
    db.session.commit()
    return jsonify({'msg':'Added'}), 201

@app.route('/api/attendance', methods=['GET', 'POST'])
def handle_attendance():
    if request.method == 'POST':
        for r in request.json:
            e = Attendance.query.filter_by(date=r['date'], student_id=r['studentId']).first()
            if e: e.status = r['status']
            else: db.session.add(Attendance(date=r['date'], student_id=r['studentId'], student_name=r['studentName'], class_name=r['className'], status=r['status']))
        db.session.commit()
        return jsonify({'msg':'Saved'}), 201
    d=request.args.get('date')
    return jsonify([r.to_dict() for r in Attendance.query.filter_by(date=d).all()]) if d else jsonify([])

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True, port=5000)