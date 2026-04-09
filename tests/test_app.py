import os
import sqlite3
import tempfile
import pytest

import app as books_app


@pytest.fixture
def client():
    db_fd, test_db_path = tempfile.mkstemp()

    books_app.app.config["TESTING"] = True
    books_app.DATABASE = test_db_path

    with books_app.app.app_context():
        books_app.init_db()

    with books_app.app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(test_db_path)


def get_all_books(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM books ORDER BY id ASC").fetchall()
    conn.close()
    return rows


def test_add_book_stores_title_author_and_image_url(client):
    response = client.post(
        "/add",
        data={
            "title": "Clean Architecture",
            "author": "Robert C. Martin",
            "image_url": "https://example.com/clean-architecture.jpg",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    page = response.data.decode("utf-8")

    assert "Clean Architecture" in page
    assert "Robert C. Martin" in page
    assert "https://example.com/clean-architecture.jpg" in page

    books = get_all_books(books_app.DATABASE)
    assert len(books) == 1
    assert books[0]["title"] == "Clean Architecture"
    assert books[0]["author"] == "Robert C. Martin"
    assert books[0]["image_url"] == "https://example.com/clean-architecture.jpg"


def test_search_by_title_returns_correct_result(client):
    client.post(
        "/add",
        data={
            "title": "Atomic Habits",
            "author": "James Clear",
            "image_url": "https://example.com/atomic.jpg",
        },
    )
    client.post(
        "/add",
        data={
            "title": "Deep Work",
            "author": "Cal Newport",
            "image_url": "https://example.com/deep-work.jpg",
        },
    )

    response = client.get("/?search=Atomic")
    page = response.data.decode("utf-8")

    assert "Atomic Habits" in page
    assert "James Clear" in page
    assert "Deep Work" not in page


def test_search_by_author_returns_correct_result(client):
    client.post(
        "/add",
        data={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "image_url": "https://example.com/clean-code.jpg",
        },
    )
    client.post(
        "/add",
        data={
            "title": "Deep Work",
            "author": "Cal Newport",
            "image_url": "https://example.com/deep-work.jpg",
        },
    )

    response = client.get("/?search=Robert%20C.%20Martin")
    page = response.data.decode("utf-8")

    assert "Clean Code" in page
    assert "Robert C. Martin" in page
    assert "Deep Work" not in page


def test_search_nonexistent_term_returns_empty_result(client):
    client.post(
        "/add",
        data={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "image_url": "https://example.com/clean-code.jpg",
        },
    )

    response = client.get("/?search=NotARealBook123")
    page = response.data.decode("utf-8")

    assert "Clean Code" not in page
    assert "No books found for that search." in page