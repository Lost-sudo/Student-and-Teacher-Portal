# Import the create_app function from the website package
from website import create_app

# Call the create_app function to create the Flask application instance
app = create_app()

# Check if the script is being executed directly
if __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(debug=True)
