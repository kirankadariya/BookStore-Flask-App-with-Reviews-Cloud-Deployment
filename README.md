# BookShelf Pro – Week 12 Deployment Project

## Student Information
- Course: CSCI 414
- Assignment: Week 12 – Deploying a Web Application to the Cloud
- Name: Kiran Kadariya
- Instructor: Jalal Khalil

## Project Description
BookShelf Pro is a Flask-based web application that allows users to:
- view books in a modern bookshelf layout
- add new books with title, author, and image URL
- search books by title or author
- add reviews for books
- view existing reviews

This project continues the earlier assignments:
- Week 6: fancy UI, real books, search, testing
- Week 7: MongoDB integration for reviews
- Week 12: cloud deployment and live review feature

## Technologies Used
- Python
- Flask
- SQLite
- MongoDB Atlas
- HTML
- CSS
- Render

## Project Structure
project-folder/
│
├── app.py
├── books.db
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    └── style.css

## Features
### Book Features
- display at least 10 real books
- show title, author, and cover image
- add new books

### Search Features
- search by title
- search by author
- show empty result when nothing matches

### Review Features
- add reviews to books
- display all existing reviews
- store reviews in MongoDB Atlas

## Local Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
