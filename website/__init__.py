from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_admin import Admin

# Create SQLAlchemy database instance
db = SQLAlchemy()

# Define database file name
DB_NAME = "studentandteacheruser.db"

# Create Flask-Admin instance
admin = Admin()

# Function to create the Flask application
def create_app():
    # Initialize Flask application
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # Set secret key for session management
    app.config['SECRET_KEY'] = 'janjan123'
    
    # Set SQLite database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    # Initialize Flask-Admin with the app
    admin.init_app(app)

    # Import blueprints for views and authentication
    from .views import views
    from .auth import auth

    # Register blueprints with the app
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    # Import User model
    from .models import User

    # Create database if it does not exist
    create_database(app)

    # Initialize LoginManager for managing user sessions
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Set login view
    login_manager.init_app(app)

    # Function to load a user given its ID
    @login_manager.user_loader
    def load_user(user_id):
        user = User.query.get(int(user_id))
        return user

    return app

# Function to create the database if it does not exist
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        # Create all tables defined in models
        with app.app_context():
            db.create_all()
        print("Database created")
