The File Structure is Something Like :

/project
    /templates
        login.html
        register.html
        search.html
        book.html
    import.py
    app.py
    books.csv
    requirements.txt
    README.md
    .env


Inside Templates There are templates For login ,register page , search and book details page. 
Inside App.py is our main flask App having all of the apis and our main backend code. 
import.py contains function to import books.csv to the database.
requirements.txt have packages which will be used entire the project.


There are SQL Queries to create table:

For Users Table:
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL
);

For Books Table:
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR(10) NOT NULL,
    title VARCHAR(100) NOT NULL,
    author VARCHAR(100) NOT NULL,
    year VARCHAR(4) NOT NULL
);

For Reviews Table :
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    book_id INTEGER REFERENCES books(id),
    comment TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Environment Variables using .env file:
.env file have postgre database Connection url.
and we are loading it using load_dotenv() 




Flask Web Framework 
Flask: A lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications. You've used it here to set up your web server, define routes, and handle HTTP requests.
User Authentication and Session Management
Flask Session: An extension for Flask that adds support for Server-side Session to your application. You've configured it to store session data on the filesystem, enabling persistent sessions across requests for individual users.

Session Management: By importing Session from flask_session and configuring it within your Flask app, you enable the application to remember users across their requests. You check for user_id in the session to determine if a user is logged in, and use this to control access to certain routes.

Database Operations with SQLAlchemy
SQLAlchemy: A SQL toolkit and Object-Relational Mapping (ORM) library for Python. You've used SQLAlchemy to handle database connections and queries securely and efficiently.

Database Connection: You create an engine connected to your PostgreSQL database using create_engine and manage sessions with scoped_session and sessionmaker bound to this engine. This setup allows you to execute database operations within your application routes.

Database Queries: You use parameterized queries with text and named parameters to interact with your database, preventing SQL injection and ensuring secure database operations.

Secure Password Handling
Hashlib for Password Hashing: You've utilized the hashlib library to hash passwords before storing them in the database, enhancing security by ensuring that plaintext passwords are never stored or transmitted.
Template Rendering
Jinja2 Templating: Flask utilizes Jinja2 for rendering templates. You've used render_template to serve HTML content that can dynamically display data based on the context provided from your routes. This allows for a dynamic and responsive user interface.
Environment Variables and Configuration
dotenv: You load environment variables from a .env file at the start of your application using load_dotenv(). This is a security best practice, keeping sensitive information, such as your database URL, out of your source code.

Configuration: You configure your Flask app and Flask-Session by setting various options directly on the app.config object. This includes configuring the session type and permanence.

Routing and View Functions
Flask Routes: You've defined multiple routes (/, /register, /login, /logout, /search, /book/<isbn>) that respond to HTTP requests. Each route is associated with a view function that handles business logic, interacts with the database, and returns responses to the client.

HTTP Methods: You distinguish between GET and POST requests in your routes to separate the display of forms from the processing of form data, adhering to RESTful principles.

Error Handling and User Feedback
Error Handling and Transactions: In your database operations, you use try-except blocks to catch exceptions, rolling back transactions if errors occur to maintain database integrity.

Flash Messages: You use Flask's flash function to provide feedback to users, such as error messages or confirmation notices.


Function Details :

Application Setup and Configuration
load_dotenv(): Loads environment variables from a .env file into the application's environment. This is used to securely manage configuration details such as the database connection string.

Flask Application Instance (app): The core of your Flask application, created by instantiating the Flask class. It's used to register routes, configure the application, and tie together the various components of your application.

Session Configuration: By configuring SESSION_PERMANENT and SESSION_TYPE, and initializing Session(app), you set up server-side session management, allowing your application to remember users across their requests.

Route Definitions and View Functions
Each route in your Flask application is defined using the @app.route decorator, specifying the URL pattern and, optionally, the HTTP methods it accepts. Here's what each route does:

/ (index): The root route that checks if a user is logged in by looking for user_id in the session. If logged in, it redirects to /search; if not, it displays a welcome message with options to log in or register.

/register: Handles both the display of the registration form (GET request) and the registration logic (POST request), including hashing the password and saving the new user in the database.

/login: Similar to /register, this route handles displaying the login form and processing login attempts, including verifying hashed passwords and setting the user's ID in the session on successful login.

/logout: Clears the user session, effectively logging out the user, and redirects to the root route.


/Search: Users can search for books by title, author, or ISBN.
/Book Details: Displays detailed information about the book, including title, author, publication year, and ISBN. This page also shows aggregated review data from Google Books (average rating and total review count) if available.
/Review Submission: Users can submit a review for a book, including a rating (1-5) and a text comment. The application prevents users from submitting multiple reviews for the same book.

Google Books API Integration:
Fetches and displays external review data for books, including the average rating and total number of reviews from Google Books


Utility Functions and Database Operations
Hashing Passwords: Using hashlib.sha256, you hash passwords before storing or comparing them, enhancing security by avoiding plain-text password storage.

Database Connection and Sessions: With create_engine and scoped_session(sessionmaker(bind=engine)), you establish a connection to your database and manage sessions, allowing for executing SQL commands and queries.

Executing Database Queries: You use db.execute() for database operations, including inserting new users, checking login credentials, searching for books, and inserting reviews. Parameterized queries (:parameter) are used to prevent SQL injection.

Error Handling and User Feedback
Exception Handling in Database Operations: You wrap database operations in try-except blocks, rolling back transactions on error to maintain data integrity.

Flash Messages: By using flash(), you provide immediate feedback to users for actions such as duplicate reviews or registration errors.

Template Rendering
render_template(): This function is used to render HTML templates, passing dynamic data to the templates for displaying user information, search results, book details, and messages.
Secure Password Handling
SHA-256 for Hashing: While SHA-256 is a secure hashing algorithm, for password hashing and verification in a real-world application, consider using a library designed for password hashing, such as Werkzeug's security utilities or Passlib, which handle salts and iterations automatically.


API Usage
To access book information programmatically:

Send a GET request to /api/<isbn>.
Replace <isbn> with the book's ISBN you're inquiring about.
The response will be a JSON object containing the book's details and review statistics.