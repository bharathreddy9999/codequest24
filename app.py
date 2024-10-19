from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Course, Teacher, Feedback, StudentCourse
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university.db'
app.config['SECRET_KEY'] = 'your_complex_secret_key'  # Use a more complex secret key
db.init_app(app)


@app.before_first_request
def initialize():
    db.create_all()  # Removed drop_all for production safety

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Input validation
        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect(url_for('student_dashboard'))

        flash("Login Failed. Check your credentials.", "danger")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("you are logging out","danger")
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/select_courses', methods=['GET', 'POST'])
def select_courses():
    if request.method == 'POST':
        selected_courses = request.form.getlist('courses')
        teacher_assignments = request.form.getlist('teachers')  # Get selected teachers
        student_id = session['user_id']  # Assuming user ID is stored in the session
        flash("Select wisely","info")
        # Clear previous selections
        StudentCourse.query.filter_by(student_id=student_id).delete()
        db.session.commit()

        # Save selected courses and assign teachers
        for course_id, teacher_id in zip(selected_courses, teacher_assignments):
            selection = StudentCourse(student_id=student_id, course_id=course_id, teacher_id=teacher_id)
            db.session.add(selection)

        db.session.commit()
        flash("Courses selected successfully!", "success")
        return redirect(url_for('student_dashboard'))

    # For GET request, retrieve all courses and teachers
    courses = Course.query.all()
    teachers = Teacher.query.all()  # Get all teachers
    return render_template('select_courses.html', courses=courses, teachers=teachers)

@app.route('/api/teachers', methods=['GET'])
def api_teachers():
    teachers = Teacher.query.all()
    teacher_list = []
    for teacher in teachers:
        teacher_data = {
            'name': teacher.name,
            'age': teacher.age,
            'bio': teacher.bio,
            'research_projects': teacher.research_projects,
            'patents': teacher.patents,
            'academic_background': teacher.academic_background,
            'subject': teacher.subject,
            'joined_date': teacher.joined_date.strftime('%Y-%m-%d'),  # Format date as string
            'average_rating': calculate_average_rating(teacher.id),
        }
        teacher_list.append(teacher_data)
    return jsonify(teacher_list)

@app.route('/teacher_profiles', methods=['GET'])
def teacher_profiles():
    teachers = Teacher.query.all()
    for teacher in teachers:
        teacher.average_rating = calculate_average_rating(teacher.id)
    return render_template('teacher_profiles.html', teachers=teachers)

@app.route('/feedback', methods=['POST'])
def feedback():
    # Check if the request contains JSON data
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400

    # Extract data from the request
    data = request.json

    # Validate required fields
    required_fields = ['student_id', 'teacher_id', 'rating', 'comments']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Create and add feedback to the database
    try:
        feedback_entry = Feedback(
            student_id=data['student_id'],
            teacher_id=data['teacher_id'],
            rating=data['rating'],
            comments=data['comments'],
            timestamp=datetime.utcnow()
        )
        db.session.add(feedback_entry)
        db.session.commit()

        # Calculate and store the average rating after feedback submission
        calculate_average_rating(data['teacher_id'])
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"error": "Failed to submit feedback", "details": str(e)}), 500

    return jsonify({"message": "Feedback submitted successfully!"}), 201

def calculate_average_rating(teacher_id):
    feedbacks = Feedback.query.filter_by(teacher_id=teacher_id).all()
    if feedbacks:
        average = sum(f.rating for f in feedbacks) / len(feedbacks)
        # Update the teacher's average rating
        teacher = Teacher.query.get(teacher_id)
        teacher.average_rating = average
        db.session.commit()  # Save the updated average rating
        return average
    return 0

@app.route('/student_dashboard')
def student_dashboard():
    user_id = session.get('user_id')  # Get the logged-in user's ID from session
    if user_id:
        user = User.query.get(user_id)  # Get user info

        # Fetch selected courses for the user
        selected_courses = StudentCourse.query.filter_by(student_id=user.id).all()
        
        # Get course details from Course model
        courses = []
        for student_course in selected_courses:
            course = Course.query.get(student_course.course_id)  # Fetch course details
            if course:
                courses.append(course)  # Add to the list if course is found

        # Debugging: Print courses to check what's being fetched
        print("Selected Courses:", courses)
    else:
        user = None
        courses = []

    return render_template('student_dashboard.html', user=user, courses=courses)


# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_email = request.form['email']
        admin_password = request.form['password']

        # Hardcoded credentials for the admin (in a real app, store securely)
        if admin_email == 'rgm@gmail.com' and admin_password == 'rgm':
            session['admin_logged_in'] = True
            flash("Admin logged in successfully!", "success")
            return redirect(url_for('admin_dashboard'))

        flash("Admin login failed. Check your credentials.", "danger")

    return render_template('admin_login.html')

# Admin dashboard route
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin/logout', methods=['GET', 'POST'])
def admin_logout():
   
    session.pop('admin_id', None) 
    return redirect(url_for('admin_login'))


# Route to add teacher
@app.route('/admin/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        bio = request.form.get('bio')
        research_projects = request.form.get('research_projects')
        patents = request.form.get('patents')
        academic_background = request.form.get('academic_background')
        subject = request.form.get('subject')
        joined_date = request.form.get('joined_date')

        # Input validation
        if not name or not age or not subject or not joined_date:
            flash("All fields are required.", "danger")
            return redirect(url_for('add_teacher'))

        try:
            joined_date = datetime.strptime(joined_date, '%Y-%m-%d')

            new_teacher = Teacher(
                name=name,
                age=age,
                bio=bio,
                research_projects=research_projects,
                patents=patents,
                academic_background=academic_background,
                subject=subject,
                joined_date=joined_date
            )
            db.session.add(new_teacher)
            db.session.commit()
            flash("Teacher added successfully!", "success")
            return redirect(url_for('admin_dashboard'))

        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")

    return render_template('add_teacher.html')

# Route to add course/subject
@app.route('/admin/add_course', methods=['GET', 'POST'])
def add_course():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form.get('name')
        course_type = request.form.get('course_type')
        subject = request.form.get('subject')  # Include the subject field

        # Ensure all fields are provided
        if not name or not course_type or not subject:
            flash("All fields are required", "danger")
            return redirect(url_for('add_course'))

        new_course = Course(
            name=name,
            course_type=course_type,
            subject=subject
        )
        db.session.add(new_course)
        db.session.commit()
        flash("Course added successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('add_course.html')

if __name__ == '__main__':
    app.run(debug=True)
