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
- Flask-SQLAlchemy 3.1.1
- SQLAlchemy 2.0.23
- PostgreSQL with psycopg2-binary 2.9.9
- Python-dotenv 1.0.1
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
4. Create .env file with your configuration:

**For Development (SQLite - Default):**
```env
SECRET_KEY=your-secret-key-here-make-it-long-and-random
# DATABASE_URL not needed - will use SQLite fallback
```

**For Production (PostgreSQL):**
```env
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### Database Setup Options

**Option 1: Quick Start (SQLite)**
The app will automatically use SQLite if no DATABASE_URL is configured. Perfect for development and testing.

**Option 2: Free Cloud PostgreSQL (Recommended for Production)**
- [Neon](https://neon.tech) - Free serverless PostgreSQL
  ```bash
  # Example Neon connection string:
  DATABASE_URL=postgresql://username:password@ep-something.us-east-1.aws.neon.tech/neondb?sslmode=require
  ```
- [Supabase](https://supabase.com) - Free PostgreSQL with additional features
- [Railway](https://railway.app) - Free tier with PostgreSQL
- [Render](https://render.com) - Free PostgreSQL database

**Important SSL Configuration:**
Most cloud PostgreSQL providers require SSL connections. Make sure your DATABASE_URL includes `?sslmode=require`:
```bash
# Correct format with SSL:
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require

# The app now uses psycopg2-binary driver which properly supports SSL connections
```

**Option 3: Local PostgreSQL**
```bash
# Install PostgreSQL locally, then create a database
brew install postgresql  # On macOS
createdb facebook_clone
# Use connection string: postgresql://username:password@localhost:5432/facebook_clone
```

5. Run the application:
```
python api/app.py
```

Or deploy with Vercel:
```
vercel dev
```

## Environment Variables

Create a `.env` file in the root directory with:

```env
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DATABASE_URL=postgresql://username:password@host:port/database_name
```

## Database Migration

This project has been migrated from SQLite to PostgreSQL with SQLAlchemy ORM for better scalability and production readiness.
