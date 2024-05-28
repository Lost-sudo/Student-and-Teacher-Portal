from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User, StudentInfo, TeacherInfo  # Importing models
from . import db  # Importing the database instance
from passlib.hash import sha256_crypt  # Importing passlib for password hashing
from flask_login import login_user, login_required, logout_user, current_user  # Importing login-related functions

# Creating a Blueprint instance named 'auth'
auth = Blueprint('auth', __name__)

# Route for user login
@auth.route('/', methods=['GET', 'POST'])
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Handling POST requests
        email = request.form.get('email')  # Getting email from form
        password = request.form.get('password')  # Getting password from form

        user = User.query.filter_by(email=email).first()  # Querying the user by email

        if user:  # If user exists
            if sha256_crypt.verify(password, user.password):  # If password matches
                login_user(user)  # Log in the user

                # Redirect to appropriate dashboard based on user role
                if user.is_student:
                    return redirect(url_for('views.home'))
                elif user.is_teacher:
                    return redirect(url_for('views.teacher_dashboard'))
                else:
                    flash("User role not specified", category='error')  # If role is not specified

            else:  # If password does not match
                flash("Incorrect email or password", category='error')

        else:  # If user with provided email not found
            flash("User with provided email not found", category='error')

    return render_template('login.html')  # Render login template

# Route for user logout
@auth.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    return redirect(url_for('auth.login'))  # Redirect to login page

# Route for student registration
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':  # Handling POST requests
        # Get form data
        firstname = request.form.get('first-name')
        lastname = request.form.get('last-name')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        course = request.form.get('course-selection')
        birthday = request.form.get('birthdate')
        gender = request.form.get('gender')

        existing_user = User.query.filter_by(email=email).first()  # Check if user already exists

        if existing_user:  # If user already exists
            flash("Email is already in use", category='error')
        elif len(firstname) == 0:  # If first name is not provided
            flash("First name is required", category='error')
        elif len(lastname) == 0:  # If last name is not provided
            flash("Last name is required", category='error')
        elif len(email) == 0:  # If email is not provided
            flash("Email is required", category='error')
        elif password1 != password2:  # If passwords do not match
            flash("Passwords do not match", category='error')
        elif len(password1) < 7:  # If password is too short
            flash("Password must be at least 7 characters long", category='error')
        else:  # If all validations pass
            hashed_password = sha256_crypt.hash(password1)  # Hash the password
            new_user = User(email=email, password=hashed_password, is_student=True)  # Create a new user
            student_info = StudentInfo(firstname=firstname, lastname=lastname, course=course, birthday=birthday, gender=gender)  # Create student info
            new_user.student_info.append(student_info)  # Add student info to user
            db.session.add(new_user)  # Add user to the session
            db.session.commit()  # Commit changes to the database
            flash('Registration successful', category='success')  # Display success message
            return redirect(url_for('auth.login'))  # Redirect to login page

    return render_template('register.html')  # Render registration template

# Route for teacher registration
@auth.route('/teacher_registration', methods=['GET', 'POST'])
def tregister():
    if request.method == 'POST':  # Handling POST requests
        # Get form data
        firstname = request.form.get('teacher-first-name')
        lastname = request.form.get('teacher-last-name')
        email = request.form.get('teacher-email')
        password1 = request.form.get('tpassword1')
        password2 = request.form.get('tpassword2')
        rank = request.form.get('rank')
        birthday = request.form.get('t-birthdate')
        gender = request.form.get('t-gender')

        existing_teacher = User.query.filter_by(email=email).first()  # Check if teacher already exists

        if existing_teacher:  # If teacher already exists
            flash("Email is already in use", category='error')
        elif len(firstname) == 0:  # If first name is not provided
            flash("First name is required", category='error')
        elif len(lastname) == 0:  # If last name is not provided
            flash("Last name is required", category='error')
        elif len(email) == 0:  # If email is not provided
            flash("Email is required", category='error')
        elif password1 != password2:  # If passwords do not match
            flash("Passwords do not match", category='error')
        elif len(password1) < 7:  # If password is too short
            flash("Password must be at least 7 characters long", category='error')
        else:  # If all validations pass
            hashed_password = sha256_crypt.hash(password1)  # Hash the password
            new_user = User(email=email, password=hashed_password, is_teacher=True)  # Create a new user
            teacher_info = TeacherInfo(firstname=firstname, lastname=lastname, rank=rank, birthday=birthday, gender=gender)  # Create teacher info
            new_user.teacher_info.append(teacher_info)  # Add student info to user
            db.session.add(new_user)  # Add user to the session
            db.session.commit()  # Commit changes to the database
            flash('Registration successful', category='success')  # Display success message
            return redirect(url_for('auth.login'))  # Redirect to login page
    return render_template('teacher_registration.html')  # Render registration template

