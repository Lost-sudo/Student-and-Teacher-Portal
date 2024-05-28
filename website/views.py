# Import necessary modules and functions
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import StudentInfo, TeacherInfo, Subjects, Enrollment, Grade, Event, NewsandUpdates, Resource
from . import db
import random
import string
from datetime import date


# Create a Blueprint named 'views'
views = Blueprint('views', __name__)

# Home route for authenticated users
@views.route('/home')
@login_required
def home():
    if current_user.is_authenticated:  # Check if the user is authenticated
        subjects = []  # Initialize an empty list for subjects
        firstname = current_user.user_id  # Default firstname to user_id
        
        if current_user.is_student:  # Check if the user is a student
            student_info = StudentInfo.query.filter_by(user_id=current_user.user_id).first()  # Fetch student info
            if student_info:
                firstname = student_info.firstname  # Get the firstname from student_info
                subjects = Subjects.query.join(Enrollment, Subjects.id == Enrollment.subject_id).filter(Enrollment.student_id == student_info.id).all()  # Get subjects the student is enrolled in
        elif current_user.is_teacher:  # Check if the user is a teacher
            teacher_info = TeacherInfo.query.filter_by(user_id=current_user.user_id).first()  # Fetch teacher info
            if teacher_info:
                firstname = teacher_info.firstname  # Get the firstname from teacher_info
                subjects = Subjects.query.filter_by(teacher_id=teacher_info.id).all()  # Get subjects the teacher is teaching

        return render_template('student/home.html', user=current_user, firstname=firstname, subjects=subjects)  # Render the home template
    else:
        flash('You are not logged in.', category='error')  # Flash message if user is not logged in
        return redirect(url_for('auth.login'))  # Redirect to login page

# Function to render news for different templates
def render_news(template):
    news_updates = NewsandUpdates.query.order_by(NewsandUpdates.news_date.desc()).all()  # Fetch all news updates ordered by date
    return render_template(template, user=current_user, news_updates=news_updates)  # Render the specified template

# News route for students
@views.route('/news')
@login_required
def news():
    return render_news('student/newsandupdates.html')  # Call render_news with the student news template

# News route for teachers
@views.route('/t-news')
@login_required
def tnews():
    return render_news('teacher/newsandupdates.html')  # Call render_news with the teacher news template

# Profile route
@views.route('/profile')
@login_required
def profile():
    if current_user.is_student:  # Check if the user is a student
        student_info = StudentInfo.query.filter_by(user_id=current_user.user_id).first()  # Fetch student info
        if student_info:
            return render_template('student/profile.html', user=current_user, student_info=student_info)  # Render student profile template
    elif current_user.is_teacher:  # Check if the user is a teacher
        teacher_info = TeacherInfo.query.filter_by(user_id=current_user.user_id).first()  # Fetch teacher info
        if teacher_info:
            return render_template('teacher/profile.html', user=current_user, teacher_info=teacher_info)  # Render teacher profile template
    else:
        flash('User type not recognized.', 'danger')  # Flash message if user type is not recognized
        return redirect(url_for('auth.login'))  # Redirect to login page

# Subjects route
@views.route('/subjects')
@login_required
def subjects():
    if current_user.is_authenticated:  # Check if the user is authenticated
        subjects = []
        if current_user.is_student:  # Check if the user is a student
            subjects = Subjects.query.join(Enrollment, Subjects.id == Enrollment.subject_id).filter(Enrollment.student_id == current_user.user_id).all()  # Get subjects the student is enrolled in
        elif current_user.is_teacher:  # Check if the user is a teacher
            teacher_info = TeacherInfo.query.filter_by(user_id=current_user.user_id).first()  # Fetch teacher info
            if teacher_info:
                subjects = Subjects.query.filter_by(teacher_id=teacher_info.id).all()  # Get subjects the teacher is teaching

        return render_template('student/subjects.html', user=current_user, subjects=subjects)  # Render subjects template
    else:
        flash('You are not logged in.', category='error')  # Flash message if user is not logged in
        return redirect(url_for('auth.login'))  # Redirect to login page

# Enrollment route for subjects
@views.route('/enroll', methods=['POST'])
@login_required
def enroll_subject():
    if request.method == 'POST':  # Check if the request method is POST
        subject_code = request.form.get('subject_code')  # Get the subject code from the form
        print(f"Received subject code: {subject_code}")
        if subject_code:
            subject = Subjects.query.filter_by(subject_code=subject_code).first()  # Query the subject using the subject code
            print(f"Subject query result: {subject}")
            if subject:
                enrollment_exists = Enrollment.query.filter_by(subject_id=subject.id, student_id=current_user.user_id).first()  # Check if the student is already enrolled
                print(f"Enrollment exists query result: {enrollment_exists}")
                if enrollment_exists:
                    flash('You are already enrolled in this subject.', 'info')  # Flash message if already enrolled
                else:
                    new_enrollment = Enrollment(subject_id=subject.id, student_id=current_user.user_id)  # Create a new enrollment
                    db.session.add(new_enrollment)
                    db.session.commit()
                    flash('Enrollment successful!', 'success')  # Flash message for successful enrollment
            else:
                flash('Invalid enrollment code.', 'danger')  # Flash message for invalid code
        else:
            flash('Please enter an enrollment code.', 'danger')  # Flash message if no code entered

    return redirect(url_for('views.home'))  # Redirect to home page

# Schedule route
@views.route('/schedule')
@login_required
def schedule():
    if current_user.is_authenticated:  # Check if the user is authenticated
        events = Event.query.all()  # Fetch all events
        upcoming_events = []
        past_events = []
        today = date.today()  # Get today's date

        for event in events:
            if event.event_date >= today:  # Check if the event is upcoming
                upcoming_events.append(event)
            else:  # Otherwise, it's a past event
                past_events.append(event)

        return render_template('student/schedule.html', user=current_user, upcoming_events=upcoming_events, past_events=past_events)  # Render schedule template
    else:
        flash('You are not logged in.', category='error')  # Flash message if user is not logged in
        return redirect(url_for('auth.login'))  # Redirect to login page

# Grades route
@views.route('/grades')
@login_required
def grades():
    if current_user.is_authenticated:  # Check if the user is authenticated
        student_info = StudentInfo.query.filter_by(user_id=current_user.user_id).first()  # Fetch student info
        if student_info:
            enrollments = Enrollment.query.filter_by(student_id=student_info.user_id).all()  # Get all enrollments for the student
            grades = []
            for enrollment in enrollments:
                subject = Subjects.query.get(enrollment.subject_id)  # Get the subject
                grade = Grade.query.filter_by(student_id=student_info.user_id, subject_id=subject.id).first()  # Get the grade for the subject
                grades.append({
                    'subject_name': subject.name,
                    'grade': grade.value if grade else 'N/A'
                })
            return render_template('student/grades.html', user=current_user, grades=grades)  # Render grades template
        else:
            flash('Student information not found.', 'danger')  # Flash message if student info not found
            return redirect(url_for('auth.login'))  # Redirect to login page
    else:
        flash('You are not logged in.', category='error')  # Flash message if user is not logged in
        return redirect(url_for('auth.login'))  # Redirect to login page
    
# Route to view resources
@views.route('/resources')
@login_required
def view_resources():
    # If the current user is a student
    if current_user.is_student:
        # Fetch student information
        student_info = StudentInfo.query.filter_by(user_id=current_user.user_id).first()
        if not student_info:
            # If student information is not found, redirect to login page with error message
            flash('Student information not found.', 'danger')
            return redirect(url_for('auth.login'))

        # Fetch subjects enrolled by the student
        subjects = Subjects.query.join(Enrollment, Subjects.id == Enrollment.subject_id)\
                                 .filter(Enrollment.student_id == student_info.id).all()
        # Render the template for student's resources, passing user and subjects
        return render_template('student/resource.html', user=current_user, subjects=subjects)

    # If the current user is a teacher
    elif current_user.is_teacher:
        # Fetch teacher information
        teacher_info = TeacherInfo.query.filter_by(user_id=current_user.user_id).first()
        if not teacher_info:
            # If teacher information is not found, redirect to login page with error message
            flash('Teacher information not found.', 'danger')
            return redirect(url_for('auth.login'))

        # Fetch subjects taught by the teacher
        subjects = Subjects.query.filter_by(teacher_id=teacher_info.id).all()
        # Render the template for teacher's resources, passing user and subjects
        return render_template('teacher/resource.html', user=current_user, subjects=subjects)

    else:
        # If user type is not recognized, redirect to login page with error message
        flash('User type not recognized.', 'danger')
        return redirect(url_for('auth.login'))


# Route to view resources by subject
@views.route('/resources/<int:subject_id>')
@login_required
def view_resources_by_subject(subject_id):
    # Fetch subject by ID or return 404 error if not found
    subject = Subjects.query.get_or_404(subject_id)
    # Fetch resources related to the subject
    resources = Resource.query.filter_by(subject_id=subject_id).all()
    # Render the template for resources by subject, passing user, subject, and resources
    return render_template('student/resource_by_subject.html', user=current_user, subject=subject, resources=resources)


# About route
@views.route('/about')
def about():
    return render_template('about.html')  # Render about template

# Teacher dashboard route
@views.route('/teacher')
@login_required
def teacher_dashboard():
    if current_user.is_authenticated:  # Check if the user is authenticated
        return render_template('teacher/home.html', teacher=current_user)  # Render teacher dashboard template
    else:
        flash('You are not logged in.', category='error')  # Flash message if user is not logged in
        return redirect(url_for('auth.login'))  # Redirect to login page

# Teacher home route
@views.route('/t-home')
@login_required
def teacher_home():
    if current_user.is_authenticated:  # Check if the user is authenticated
        teacher_info = TeacherInfo.query.filter_by(user_id=current_user.user_id).first()  # Fetch teacher info
        if teacher_info:
            firstname = teacher_info.firstname  # Get the firstname of the teacher
            return render_template('teacher/home.html', teacher=current_user, firstname=firstname)  # Render teacher home template
        else:
            flash('Teacher information not found.', 'danger')  # Flash message if teacher info not found
            return redirect(url_for('auth.login'))  # Redirect to login page
    else:
        flash('You are not logged in.', category='error')  # Flash message if user is not logged in
        return redirect(url_for('auth.login'))  # Redirect to login page


# Teacher subjects route
@views.route('/t-subjects')
@login_required
def teacher_subjects():
    if current_user.is_authenticated:  # Check if the user is authenticated
        teacher_info = TeacherInfo.query.filter_by(user_id=current_user.user_id).first()  # Fetch teacher info
        if teacher_info:
            subjects = Subjects.query.filter_by(teacher_id=teacher_info.id).all()  # Get subjects the teacher is teaching
            return render_template('teacher/subjects.html', teacher=current_user, subjects=subjects)  # Render teacher subjects template
        else:
            flash('Teacher information not found.', 'danger')  # Flash message if teacher info not found
            return redirect(url_for('auth.login'))  # Redirect to login page
    else:
        flash('You are not logged in.', category='error')  # Flash message if user is not logged in
        return redirect(url_for('auth.login'))  # Redirect to login page

# Function to generate a unique subject code
def generate_unique_code():
    while True:
        code = ''.join(random.choices(string.digits, k=8))  # Generate an 8-digit code
        if not Subjects.query.filter_by(subject_code=code).first():  # Ensure the code is unique
            return code

# Route to create subjects for teachers
@views.route('/t-create-subjects', methods=['GET', 'POST'])
@login_required
def create_subject():
    if request.method == 'POST':  # Check if the request method is POST
        subject_name = request.form.get('subjectName')  # Get the subject name from the form
        if subject_name:
            teacher_info = TeacherInfo.query.filter_by(user_id=current_user.user_id).first()  # Fetch teacher info
            if teacher_info:
                subject_code = generate_unique_code()  # Generate a unique subject code
                new_subject = Subjects(name=subject_name, teacher_id=teacher_info.id, subject_code=subject_code)  # Create a new subject
                db.session.add(new_subject)
                db.session.commit()
                flash('Subject created successfully! Enrollment code: {}'.format(subject_code), 'success')  # Flash message for successful creation
            else:
                flash('Teacher information not found.', 'danger')  # Flash message if teacher info not found
        else:
            flash('Subject name cannot be empty.', 'danger')  # Flash message if subject name is empty

    teacher_info = TeacherInfo.query.filter_by(user_id=current_user.user_id).first()  # Fetch teacher info
    subjects = Subjects.query.filter_by(teacher_id=teacher_info.id).all() if teacher_info else []  # Get subjects if teacher info exists

    return render_template('teacher/create-subject.html', teacher=current_user, subjects=subjects)  # Render create subject template

# Schedule route for teachers
@views.route('/t-schedule')
@login_required
def tschedule():
    if current_user.is_authenticated:  # Check if the user is authenticated
        events = Event.query.all()  # Fetch all events
        upcoming_events = []
        past_events = []
        today = date.today()  # Get today's date

        for event in events:
            if event.event_date >= today:  # Check if the event is upcoming
                upcoming_events.append(event)
            else:  # Otherwise, it's a past event
                past_events.append(event)

        return render_template('teacher/schedule.html', user=current_user, upcoming_events=upcoming_events, past_events=past_events)  # Render teacher schedule template
    else:
        flash('You are not logged in.', category='error')  # Flash message if user is not logged in
        return redirect(url_for('auth.login'))  # Redirect to login page

# Grades route for teachers
@views.route('/t-grades', methods=['GET', 'POST'])
@login_required
def teacher_grades():
    teacher_info = TeacherInfo.query.filter_by(user_id=current_user.user_id).first()  # Fetch teacher info
    if not teacher_info:
        flash('Teacher information not found.', 'danger')  # Flash message if teacher info not found
        return redirect(url_for('auth.login'))  # Redirect to login page

    subjects = Subjects.query.filter_by(teacher_id=teacher_info.id).all()  # Get subjects the teacher is teaching

    student_grades = {}
    for subject in subjects:
        student_grades[subject.id] = {
            'subject_name': subject.name,
            'students': []
        }
        enrollments = Enrollment.query.filter_by(subject_id=subject.id).all()  # Get all enrollments for the subject
        for enrollment in enrollments:
            student = StudentInfo.query.get(enrollment.student_id)  # Get student info
            if student:
                grade = Grade.query.filter_by(student_id=student.user_id, subject_id=subject.id).first()  # Get the grade for the student
                student_grades[subject.id]['students'].append({
                    'student_firstname': student.firstname,
                    'student_lastname': student.lastname,
                    'grade': grade.value if grade else 'N/A'
                })
            else:
                student_grades[subject.id]['students'].append({
                    'student_firstname': 'Unknown',
                    'student_lastname': 'Student',
                    'grade': 'N/A'
                })

    if request.method == 'POST':  # Check if the request method is POST
        student_firstname = request.form.get('studentFirstName')  # Get student first name from the form
        student_lastname = request.form.get('studentLastName')  # Get student last name from the form
        subject_id = request.form.get('subject')  # Get subject ID from the form
        grade_value = request.form.get('grade')  # Get grade value from the form

        try:
            grade_value = float(grade_value)  # Convert grade value to float
        except ValueError:
            flash('Invalid grade value.', 'danger')  # Flash message if grade value is invalid
            return redirect(url_for('views.teacher_grades'))

        student = StudentInfo.query.filter_by(firstname=student_firstname, lastname=student_lastname).first()  # Fetch student by first and last name
        if student:
            grade = Grade.query.filter_by(student_id=student.user_id, subject_id=subject_id).first()  # Fetch grade
            if grade:
                grade.value = grade_value  # Update grade value
            else:
                new_grade = Grade(student_id=student.user_id, subject_id=subject_id, value=grade_value)  # Create a new grade
                db.session.add(new_grade)
            db.session.commit()
            flash('Grade updated successfully!', 'success')  # Flash message for successful update
        else:
            flash('Student not found.', 'danger')  # Flash message if student not found

    return render_template('teacher/grades.html', teacher=current_user, student_grades=student_grades)  # Render teacher grades template

@views.route('/t-post-resource', methods=['GET', 'POST'])
@login_required
def post_resource():
    # Ensure the user is logged in
    if not current_user.is_teacher:
        # If the user is not a teacher, show an error message and redirect to the home page
        flash('Access denied.', 'danger')
        return redirect(url_for('views.home'))

    # Fetch the teacher's information from the database using the current user's ID
    teacher_info = TeacherInfo.query.filter_by(user_id=current_user.user_id).first()
    if not teacher_info:
        # If no teacher information is found, show an error message and redirect to the login page
        flash('Teacher information not found.', 'danger')
        return redirect(url_for('auth.login'))

    # Fetch the subjects associated with the teacher
    subjects = Subjects.query.filter_by(teacher_id=teacher_info.id).all()

    if request.method == 'POST':
        # Get the form data
        title = request.form.get('title')
        description = request.form.get('description')
        url = request.form.get('url')
        subject_id = request.form.get('subject_id')

        # Check if all required fields are filled
        if not title or not url or not subject_id:
            # If any required field is missing, show an error message and redirect back to the form
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('views.post_resource'))

        # Create a new Resource object with the form data
        new_resource = Resource(
            title=title,
            description=description,
            url=url,
            subject_id=subject_id,
            teacher_id=teacher_info.id
        )

        # Add the new resource to the database session and commit it
        db.session.add(new_resource)
        db.session.commit()

        # Show a success message and redirect to the teacher's dashboard
        flash('Resource posted successfully!', 'success')
        return redirect(url_for('views.teacher_dashboard'))

    # Render the resource posting form template, passing the current user and their subjects
    return render_template('teacher/post_resource.html', teacher=current_user, subjects=subjects)
