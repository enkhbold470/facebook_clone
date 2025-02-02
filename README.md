# Facemash - Social Media Application - Facebook lite Clone
![gif of demo](https://github.com/user-attachments/assets/e4add8ad-5ff6-44ad-b546-31caa6f3789e)

A social media platform built with Flask that allows users to share posts, images, and interact with other users.

## Features

- User authentication (register/login/logout)
- Profile management with customizable:
  - Profile pictures
  - Bio
  - Location
  - First and Last name
- News feed
- Create posts with text and images
- View user profiles
- Responsive design using Tailwind CSS

## Tech Stack

- Flask 3.1.0
- Flask-Login 0.6.3
- Python-dotenv 1.0.1
- SQLite database
- Tailwind CSS
- Gunicorn 23.0.0 (Production server)

## Installation

1. Clone the repository
2. Create a virtual environment or you can use conda env:
```python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Create .env file
```
cp .env.example .env
```
5. Voila! that is it: 
```
python app.py
```
