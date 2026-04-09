import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g
from pymongo import MongoClient

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), "books.db")

mongo_client = MongoClient("mongodb://localhost:27017/")
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
            "https://images-na.ssl-images-amazon.com/images/I/41jEbK-jG+L._SX374_BO1,204,203,200_.jpg",
        ),
        (
            "The Pragmatic Programmer",
            "Andrew Hunt, David Thomas",
            "https://images-na.ssl-images-amazon.com/images/I/518FqJvR9aL._SX380_BO1,204,203,200_.jpg",
        ),
        (
            "Atomic Habits",
            "James Clear",
            "https://images-na.ssl-images-amazon.com/images/I/513Y5o-DYtL._SX328_BO1,204,203,200_.jpg",
        ),
        (
            "Deep Work",
            "Cal Newport",
            "https://images-na.ssl-images-amazon.com/images/I/41-sN-mzwKL._SX331_BO1,204,203,200_.jpg",
        ),
        (
            "The Clean Coder",
            "Robert C. Martin",
            "https://images-na.ssl-images-amazon.com/images/I/41xShlnTZTL._SX374_BO1,204,203,200_.jpg",
        ),
        (
            "Refactoring",
            "Martin Fowler",
            "https://images-na.ssl-images-amazon.com/images/I/41j9l3ZJ4vL._SX396_BO1,204,203,200_.jpg",
        ),
        (
            "Design Patterns",
            "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
            "https://images-na.ssl-images-amazon.com/images/I/51kuc0iWo5L._SX342_SY445_QL70_ML2_.jpg",
        ),
        (
            "Python Crash Course",
            "Eric Matthes",
            "https://images-na.ssl-images-amazon.com/images/I/51W1sBPO7tL._SX377_BO1,204,203,200_.jpg",
        ),
        (
            "Eloquent JavaScript",
            "Marijn Haverbeke",
            "https://images-na.ssl-images-amazon.com/images/I/91asIC1fRwL.jpg",
        ),
        (
            "You Don't Know JS Yet",
            "Kyle Simpson",
            "https://images-na.ssl-images-amazon.com/images/I/81kqrwS1nNL.jpg",
        ),
    ]

    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO books (title, author, image_url) VALUES (?, ?, ?)",
            books
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
        books = db.execute("SELECT * FROM books ORDER BY title ASC").fetchall()

    books_with_reviews = []
    for book in books:
        reviews = list(reviews_collection.find({"book_id": book["id"]}))
        books_with_reviews.append({
            "id": book["id"],
            "title": book["title"],
            "author": book["author"],
            "image_url": book["image_url"],
            "reviews": reviews
        })

    return render_template("index.html", books=books_with_reviews, search=search)


@app.route("/add", methods=["POST"])
def add_book():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    image_url = request.form.get("image_url", "").strip()

    if title and author and image_url:
        db = get_db()
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
        reviews_collection.insert_one({
            "book_id": book_id,
            "reviewer": reviewer,
            "review_text": review_text
        })

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    seed_books()
    app.run(debug=True)