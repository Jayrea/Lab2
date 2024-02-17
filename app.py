from flask import Flask, render_template, request, redirect, session, flash ,jsonify
from flask_session import Session 
from sqlalchemy import create_engine , text
from sqlalchemy.orm import scoped_session, sessionmaker 
import hashlib
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DATABASE_URL = os.getenv("DATABASE_URL", "default_fallback_database_url")
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

def get_google_books_data(isbn):
    try:
        response = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": f"isbn:{isbn}"})
        data = response.json()
        if data['totalItems'] > 0:
            item = data['items'][0]['volumeInfo']
            return {
                "averageRating": item.get('averageRating'),
                "ratingsCount": item.get('ratingsCount')
            }
    except Exception as e:
        print(f"Error fetching Google Books data: {e}")
    return None


@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/search")
    return "Welcome! Please <a href='/login'>log in</a> or <a href='/register'>register</a>."

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        try:
            db.execute(text(f"INSERT INTO users (username, password) VALUES (:username, :password)"),
           {"username": username, "password": hashed_pw})
            db.commit()
            return redirect("/login")
        except Exception as e:
            db.rollback()
            return "Registration failed. Error: " + str(e)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        user = db.execute(text("SELECT * FROM users WHERE username = :username AND password = :password"),
                          {"username": username, "password": hashed_pw}).fetchone()
        if user:
            session["user_id"] = user.id
            return redirect("/")
        else:
            return "Invalid username or password."
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/search", methods=["GET", "POST"])
def search():
    if "user_id" not in session:
        return redirect("/login")
    
    if request.method == "POST":
        query = request.form.get("query")
        query = "%" + query + "%"
        books = db.execute(text("SELECT * FROM books WHERE \
                            isbn LIKE :query OR \
                            title LIKE :query OR \
                            author LIKE :query"),
                            {"query": query}).fetchall()
        if not books:
            return render_template("search.html", message="No matches found.")
        return render_template("search.html", books=books)
    
    return render_template("search.html")

from flask import flash, redirect, render_template, request, session
from sqlalchemy import text

@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):
    if "user_id" not in session:
        return redirect("/login")

    book = db.execute(text("SELECT * FROM books WHERE isbn = :isbn"), {"isbn": isbn}).fetchone()
    if book is None:
        return "Book not found."

    if request.method == "POST":
        user_id = session["user_id"]
        rating = request.form.get("rating")
        comment = request.form.get("comment")

        existing_review = db.execute(text("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id"),
                                     {"user_id": user_id, "book_id": book.id}).fetchone()
        if existing_review:
            flash("You've already submitted a review for this book.")
        else:

            db.execute(text("INSERT INTO reviews (user_id, book_id, comment, rating) VALUES (:user_id, :book_id, :comment, :rating)"),
                       {"user_id": user_id, "book_id": book.id, "comment": comment, "rating": rating})
            db.commit()
            flash("Your review has been submitted.")

    google_books_data = get_google_books_data(isbn)
    reviews = db.execute(text("""SELECT reviews.*, users.username FROM reviews 
                                 JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id"""),
                         {"book_id": book.id}).fetchall()

    return render_template("book.html", book=book, reviews=reviews, google_books=google_books_data)


@app.route("/api/<isbn>")
def book_api(isbn):
    book = db.execute(text("SELECT * FROM books WHERE isbn = :isbn"), {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 404

    google_books_data = get_google_books_data(isbn)
    
    response = {
        "title": book.title,
        "author": book.author,
        "publishedDate": book.published_date,
        "ISBN_10": isbn,
        "ISBN_13": book.isbn13,
        "reviewCount": google_books_data.get("ratingsCount", 0) if google_books_data else 0,
        "averageRating": google_books_data.get("averageRating", 0) if google_books_data else 0
    }
    
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
