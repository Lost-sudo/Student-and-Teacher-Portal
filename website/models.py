# Import necessary modules and functions
from . import db, admin  # Importing db and admin from the current package
from flask_login import UserMixin  # Import UserMixin from flask_login for user management
from flask_admin.contrib.sqla import ModelView  # Import ModelView for Flask-Admin integration
from sqlalchemy import ForeignKey  # Import ForeignKey for creating relationships between tables
from sqlalchemy.orm import relationship  # Import relationship for ORM relationships
from datetime import datetime

# Define the User model
class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)  # Primary key
    email = db.Column(db.String(225), nullable=False)  # Email field
    password = db.Column(db.String(225), nullable=False)  # Password field
    is_student = db.Column(db.Boolean(), default=False)  # Boolean to check if the user is a student
    is_teacher = db.Column(db.Boolean(), default=True)  # Boolean to check if the user is a teacher
    is_active = db.Column(db.Boolean(), default=True)  # Boolean to check if the user is active

    def get_id(self):
        return str(self.user_id)  # Override get_id method to return user_id as a string

# Define the StudentInfo model
class StudentInfo(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.Integer, ForeignKey('user.user_id'), nullable=False)  # Foreign key to User model
    user = relationship("User", backref="student_info")  # Relationship to User model
    firstname = db.Column(db.String(225), nullable=False)  # First name
    lastname = db.Column(db.String(225), nullable=False)  # Last name
    course = db.Column(db.String(225), nullable=False)  # Course
    birthday = db.Column(db.String(225), nullable=False)  # Birthday
    gender = db.Column(db.String(20), nullable=False)  # Gender

# Define the TeacherInfo model
class TeacherInfo(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.Integer, ForeignKey('user.user_id'), nullable=False)  # Foreign key to User model
    user = relationship("User", backref="teacher_info")  # Relationship to User model
    firstname = db.Column(db.String(225), nullable=False)  # First name
    lastname = db.Column(db.String(225), nullable=False)  # Last name
    rank = db.Column(db.String, nullable=False)  # Rank
    birthday = db.Column(db.String(225), nullable=False)  # Birthday
    gender = db.Column(db.String(20), nullable=False)  # Gender

# Define the Subjects model
class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(225), nullable=False)  # Subject name
    teacher_id = db.Column(db.Integer, ForeignKey('teacher_info.user_id'), nullable=False)  # Foreign key to TeacherInfo model
    teacher = relationship("TeacherInfo", backref="subjects")  # Relationship to TeacherInfo model
    subject_code = db.Column(db.String(8), nullable=False, unique=True)  # Unique subject code

# Define the Enrollment model
class Enrollment(db.Model):
    __tablename__ = 'enrollments'  # Explicitly define the table name
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.user_id'), nullable=False)  # Foreign key to StudentInfo model
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)  # Foreign key to Subjects model

# Define the Grade model
class Grade(db.Model):
    __tablename__ = 'grades'  # Explicitly define the table name
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.user_id'), nullable=False)  # Foreign key to StudentInfo model
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)  # Foreign key to Subjects model
    value = db.Column(db.Integer, nullable=False)  # Grade value

# Define the Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    event_details = db.Column(db.Text, nullable=False)  # Event details
    event_date = db.Column(db.Date, nullable=False)  # Event date

# Define the NewsandUpdates model
class NewsandUpdates(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    news_details = db.Column(db.Text, nullable=False)  # News details
    news_date = db.Column(db.Date, nullable=False)  # News date
    update_details = db.Column(db.Text, nullable=False)  # Update details
    update_date = db.Column(db.Date, nullable=False)  # Update date

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(255), nullable=False)
    date_posted = db.Column(db.DateTime, default=db.func.current_timestamp())
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_info.id'), nullable=False)

    subject = db.relationship('Subjects', backref='resources')
    teacher = db.relationship('TeacherInfo', backref='resources')

# Add models to Flask-Admin interface
admin.add_view(ModelView(User, db.session))  # Add User model to admin
admin.add_view(ModelView(StudentInfo, db.session))  # Add StudentInfo model to admin
admin.add_view(ModelView(TeacherInfo, db.session))  # Add TeacherInfo model to admin
admin.add_view(ModelView(Subjects, db.session))  # Add Subjects model to admin
admin.add_view(ModelView(Enrollment, db.session))  # Add Enrollment model to admin
admin.add_view(ModelView(Grade, db.session))  # Add Grade model to admin
admin.add_view(ModelView(Event, db.session))  # Add Event model to admin
admin.add_view(ModelView(NewsandUpdates, db.session))  # Add NewsandUpdates model to admin
