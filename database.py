from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# --- AUTH ---
class Teacher(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    notepad = db.Column(db.Text, default="") 
    def to_dict(self): return {'id': self.id, 'name': self.name, 'email': self.email, 'notepad': self.notepad}

# --- CLASS & STUDENTS ---
class Class(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    coordinator_name = db.Column(db.String(120), nullable=False)
    coordinator_phone = db.Column(db.String(20))
    students = db.relationship('Student', backref='class', lazy=True, cascade="all, delete-orphan")
    def to_dict(self): return {'id': self.id, 'name': self.name, 'coordinatorName': self.coordinator_name, 'coordinatorPhone': self.coordinator_phone, 'students': [s.to_dict() for s in self.students]}

class Student(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    roll = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(200), default='')
    status = db.Column(db.String(50), default='Day Scholar')
    email = db.Column(db.String(120), default='')
    phone = db.Column(db.String(20), default='')
    parent_email = db.Column(db.String(120), default='')
    parent_phone = db.Column(db.String(20), default='')
    class_id = db.Column(db.String(80), db.ForeignKey('class.id'), nullable=False)
    # Relationships for analytics
    scores = db.relationship('Score', backref='student', lazy=True, cascade="all, delete-orphan")
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'roll': self.roll, 'status': self.status, 'email': self.email, 'phone': self.phone, 'parentEmail': self.parent_email, 'parentPhone': self.parent_phone}

# --- TIMETABLE ---
class Timetable(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    teacher = db.Column(db.String(100))
    location = db.Column(db.String(100))
    def to_dict(self): return {'id': self.id, 'day': self.day, 'time': self.time, 'subject': self.subject, 'teacher': self.teacher, 'location': self.location}

# --- NOTIFICATIONS ---
class Notification(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
    def to_dict(self): return {'id': self.id, 'message': self.message, 'className': self.class_name, 'timestamp': self.timestamp}

# --- ATTENDANCE ---
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    student_id = db.Column(db.String(80), db.ForeignKey('student.id'), nullable=False)
    student_name = db.Column(db.String(120), nullable=False)
    class_name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    def to_dict(self): return {'id': self.id, 'date': self.date, 'studentId': self.student_id, 'status': self.status}

# --- NEW: EXAMS & SCORES ---
class Exam(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    title = db.Column(db.String(100), nullable=False) # e.g., "Unit Test 1"
    total_marks = db.Column(db.Integer, nullable=False)
    def to_dict(self): return {'id': self.id, 'title': self.title, 'totalMarks': self.total_marks}

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.String(80), db.ForeignKey('exam.id'), nullable=False)
    student_id = db.Column(db.String(80), db.ForeignKey('student.id'), nullable=False)
    marks_obtained = db.Column(db.String(20), default="0") # String to allow "Ab" (Absent) or numbers
    
    def to_dict(self): return {'examId': self.exam_id, 'studentId': self.student_id, 'marks': self.marks_obtained}