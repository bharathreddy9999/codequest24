from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'  # Ensure this matches your actual table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Define relationships to StudentCourse
    selected_courses = relationship('StudentCourse', backref='user', lazy=True)

class Course(db.Model):
    __tablename__ = 'courses'  # Ensure this matches your actual table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    course_type = db.Column(db.String(50))
    subject = db.Column(db.String(100))  # Fixed case

    # Relationship to StudentCourse
    student_courses = relationship('StudentCourse', back_populates='course', cascade='all, delete-orphan')

class Teacher(db.Model):
    __tablename__ = 'teachers'  # Ensure this matches your actual table name
    id = db.Column(db.Integer, primary_key=True)
    available = db.Column(db.Integer, default=1, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    bio = db.Column(db.String(500), nullable=True)
    research_projects = db.Column(db.String(500), nullable=True)
    patents = db.Column(db.String(500), nullable=True)
    academic_background = db.Column(db.String(500), nullable=True)
    subject = db.Column(db.String(100), nullable=False)  # Ensure this field is populated
    joined_date = db.Column(db.Date, nullable=False)
    average_rating = db.Column(db.Float, default=0)

    feedbacks = db.relationship('Feedback', backref='teacher', lazy=True)

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Ensure 'users' matches the actual table name
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))  # Ensure 'teachers' matches the actual table name
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref='feedbacks')

class StudentCourse(db.Model):
    __tablename__ = 'student_course'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Correct ForeignKey
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)  # Correct ForeignKey
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)  # Correct ForeignKey
    
    student = db.relationship('User', backref='student_courses')
    course = db.relationship('Course', back_populates='student_courses')  # Correct relationship to Course
    teacher = db.relationship('Teacher', backref='student_courses')  # Correct relationship to Teacher
