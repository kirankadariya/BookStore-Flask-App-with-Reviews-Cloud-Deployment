import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g
from pymongo import MongoClient

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(BASE_DIR, "books.db")

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["books_web_app"]
reviews_collection = mongo_db["reviews"]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            image_url TEXT NOT NULL
        )
        """
    )

    db.commit()
    db.close()


def seed_books():
    books = [
        (
            "Clean Code",
            "Robert C. Martin",
            "https://m.media-amazon.com/images/I/41SH-SvWPxL.jpg",
        ),
        (
            "Atomic Habits",
            "James Clear",
            "https://m.media-amazon.com/images/I/91bYsX41DVL.jpg",
        ),
        (
            "Deep Work",
            "Cal Newport",
            "https://m.media-amazon.com/images/I/71g2ednj0JL.jpg",
        ),
        (
            "The Pragmatic Programmer",
            "Andrew Hunt and David Thomas",
            "https://m.media-amazon.com/images/I/518FqJvR9aL.jpg",
        ),
        (
            "Refactoring",
            "Martin Fowler",
            "https://m.media-amazon.com/images/I/81HBLf9wHCL.jpg",
        ),
        (
            "Design Patterns",
            "Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides",
            "https://m.media-amazon.com/images/I/81gtKoapHFL.jpg",
        ),
        (
            "Python Crash Course",
            "Eric Matthes",
            "https://m.media-amazon.com/images/I/71NUZ+rHNFL.jpg",
        ),
        (
            "Eloquent JavaScript",
            "Marijn Haverbeke",
            "https://m.media-amazon.com/images/I/91asIC1fRwL.jpg",
        ),
        (
            "The Hobbit",
            "J.R.R. Tolkien",
            "https://m.media-amazon.com/images/I/91b0C2YNSrL.jpg",
        ),
        (
            "1984",
            "George Orwell",
            "https://m.media-amazon.com/images/I/71kxa1-0mfL.jpg",
        ),
        (
           "Man’s Search for Meaning",
           "Viktor E. Frankl",
           "https://m.media-amazon.com/images/I/71tbalAHYCL.jpg",

        ),
        (   "The Body Keeps the Score",
            "Bessel van der Kolk",
            "https://m.media-amazon.com/images/I/71HMyqG6MRL.jpg",
         ),
    ]

    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    # Insert default books only if they do not already exist
    for title, author, image_url in books:
        cursor.execute(
            """
            SELECT id FROM books
            WHERE LOWER(title) = LOWER(?) AND LOWER(author) = LOWER(?)
            """,
            (title, author),
        )
        existing = cursor.fetchone()

        if not existing:
            cursor.execute(
                "INSERT INTO books (title, author, image_url) VALUES (?, ?, ?)",
                (title, author, image_url),
            )

    # Remove duplicate rows, keep the oldest one
    cursor.execute(
        """
        DELETE FROM books
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM books
            GROUP BY LOWER(title), LOWER(author)
        )
        """
    )

    db.commit()
    db.close()


@app.route("/", methods=["GET"])
def index():
    search = request.args.get("search", "").strip()
    db = get_db()

    if search:
        like_term = f"%{search}%"
        books = db.execute(
            """
            SELECT * FROM books
            WHERE LOWER(title) LIKE LOWER(?)
               OR LOWER(author) LIKE LOWER(?)
            ORDER BY title ASC
            """,
            (like_term, like_term),
        ).fetchall()
    else:
        books = db.execute(
            "SELECT * FROM books ORDER BY title ASC"
        ).fetchall()

    books_with_reviews = []
    for book in books:
        reviews = list(reviews_collection.find({"book_id": book["id"]}))
        books_with_reviews.append(
            {
                "id": book["id"],
                "title": book["title"],
                "author": book["author"],
                "image_url": book["image_url"],
                "reviews": reviews,
            }
        )

    return render_template("index.html", books=books_with_reviews, search=search)


@app.route("/add", methods=["POST"])
def add_book():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    image_url = request.form.get("image_url", "").strip()

    if title and author and image_url:
        db = get_db()

        existing = db.execute(
            """
            SELECT id FROM books
            WHERE LOWER(title) = LOWER(?) AND LOWER(author) = LOWER(?)
            """,
            (title, author),
        ).fetchone()

        if not existing:
            db.execute(
                "INSERT INTO books (title, author, image_url) VALUES (?, ?, ?)",
                (title, author, image_url),
            )
            db.commit()

    return redirect(url_for("index"))


@app.route("/add_review/<int:book_id>", methods=["POST"])
def add_review(book_id):
    reviewer = request.form.get("reviewer", "").strip()
    review_text = request.form.get("review_text", "").strip()

    if reviewer and review_text:
        reviews_collection.insert_one(
            {
                "book_id": book_id,
                "reviewer": reviewer,
                "review_text": review_text,
            }
        )

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    seed_books()
    app.run(debug=True)