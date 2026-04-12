# BookShelf Pro – Week 12 Deployment Project

## Student Information
- Course: CSCI 414
- Assignment: Week 12 – Deploying a Web Application to the Cloud
- Name: Kiran Kadariya
- Instructor: Jalal Khalil

Live Application
https://bookstore-flask-app-with-reviews-cloud.onrender.com

Project Overview
This project is a Flask-based web application deployed to the cloud.
The application allows users to:

- View a list of books
- Add reviews to books
- View existing reviews

Technologies Used
- Python
- Flask
- SQLite (Books)
- MongoDB Atlas (Reviews)
- HTML / CSS
- Render (Cloud Deployment)

Features
Book Listing
- Displays books with title, author, and cover image

Review Feature
- Users can add reviews for a book
- Users can view reviews
- Reviews are stored in MongoDB Atlas

Cloud Deployment
- Application is publicly accessible
- Hosted on Render

How to Run Locally
pip install -r requirements.txt
python app.py

MongoDB Setup
- Created MongoDB Atlas cluster
- Added IP access (0.0.0.0/0)
- Created database user
- Used connection string via environment variable

Deployment
- Deployed using Render Web Service
- Build command: pip install -r requirements.txt
- Start command: gunicorn app:app
- Environment variable: MONGO_URI

Testing
- App loads from public URL
- Books display correctly
- Reviews can be added
- Reviews persist after refresh


Conclusion
This project demonstrates deploying a Flask application to the cloud with a working MongoDB-based review system.
