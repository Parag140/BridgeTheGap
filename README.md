Flask User Authentication System :

This project is a Flask-based web application that implements a user registration and login system.
It uses MongoDB as the database to store user credentials securely and provides functionality for users to register, log in, and navigate to a home page upon successful authentication.                   

 Features
1.User Registration:
Users can register by providing their details, which are securely stored in the MongoDB database.

2.User Login:
Users can log in by entering their credentials. The system verifies the credentials against the database.

3.Authentication:
If the credentials match, users are redirected to the home page.


Here’s a sample README file for your project:

Flask User Authentication System
This project is a Flask-based web application that implements a user registration and login system. It uses MongoDB as the database to store user credentials securely and provides functionality for users to register, log in, and navigate to a home page upon successful authentication.

Features:
User Registration:
Users can register by providing their details, which are securely stored in the MongoDB database.

User Login:
Users can log in by entering their credentials. The system verifies the credentials against the database.

Authentication:
If the credentials match, users are redirected to the home page.

Technologies Used :
1.Flask: A lightweight Python web framework for building web applications.
2.MongoDB: A NoSQL database for storing user credentials.
3.HTML/CSS: For building the front-end interface of the pages.
4.Python: For back-end logic.

Prerequisites :
Ensure the following are installed on your system:

Python (version 3.6 or above)
MongoDB (local or hosted on a cloud service like MongoDB Atlas)
Required Python libraries:
Flask
Flask-PyMongo
Flask-WTF (for forms)
Werkzeug (for secure password handling)
Install the dependencies using the command:

bash
Copy code
pip install flask flask-pymongo flask-wtf werkzeug
Setup and Usage
Clone the Repository:

bash
Copy code
git clone <repository_url>
cd flask-user-authentication
Run MongoDB:
Ensure your MongoDB server is running locally or update the connection string in the Flask app for a hosted MongoDB instance.

Set Up the Application:
Update the app.py file with your MongoDB connection string and ensure the database and collection names are consistent.

Run the Application:
Start the Flask server by running:

bash
Copy code
python app.py
The application will be accessible at http://127.0.0.1:5000.

Register and Log In:

Navigate to the /register route to register a new user.
Navigate to the /login route to log in with your credentials.
Folder Structure
csharp
Copy code
flask-user-authentication/
│
├── templates/            # HTML templates (register.html, login.html, home.html)
├── static/               # Static files (CSS, JS, images)
├── app.py                # Main Flask application
├── requirements.txt      # List of dependencies
└── README.md             # Project overview (this file)

Developed by Shaik Faheem Ahamad


