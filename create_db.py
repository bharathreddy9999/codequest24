from app import app, db
from models import User, Course, Teacher

with app.app_context():
    db.create_all()

    # Create a default user if none exists
    if not User.query.first():
        user = User(name='John Doe', email='john@example.com', password='password')  # Use hashed password
        db.session.add(user)

    # Create default courses if none exist
    if not Course.query.first():
        courses = [
            Course(name='Data Structures', course_type='Theory'),
            Course(name='Database Systems', course_type='Theory'),
            Course(name='Operating Systems', course_type='Theory'),
            Course(name='Computer Networks', course_type='Theory'),
            Course(name='Software Engineering', course_type='Theory'),
            Course(name='Web Development', course_type='Lab'),
            Course(name='Database Lab', course_type='Lab')
        ]
        db.session.add_all(courses)

    # Create default teachers if none exist
    if not Teacher.query.first():
        teachers = [
            Teacher(name='Dr. Smith', bio='Expert in Algorithms', research_projects='Algorithm Optimization', patents='None', academic_background='PhD in Computer Science'),
            Teacher(name='Prof. Johnson', bio='Database Management Specialist', research_projects='Database Security', patents='US1234567', academic_background='MSc in Computer Science')
        ]
        db.session.add_all(teachers)

    # Commit all changes to the database
    db.session.commit()
