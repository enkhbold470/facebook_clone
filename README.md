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

- **Backend:** Flask 3.1.0, Flask-Login 0.6.3, Flask-SQLAlchemy 3.1.1
- **Database:** PostgreSQL with hybrid driver support (psycopg2-binary/pg8000)
- **File Storage:** Vercel Blob Storage with local fallback
- **Authentication:** Flask-Login with password hashing
- **Frontend:** Tailwind CSS, Responsive design
- **Deployment:** Vercel (serverless) with Gunicorn/Waitress fallback
- **Environment:** Python-dotenv for configuration

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

**For Production (PostgreSQL + Vercel Blob Storage):**
```env
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DATABASE_URL=postgresql://username:password@host:port/database_name
BLOB_READ_WRITE_TOKEN=vercel_blob_rw_xxxxxxxxxxxxxxxxxxxxxxxxxx
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

### File Storage Options

**Option 1: Vercel Blob Storage (Recommended for Production)**
For production deployments on Vercel, the app automatically uses [Vercel Blob Storage](https://vercel.com/docs/storage/vercel-blob) when the `BLOB_READ_WRITE_TOKEN` is configured:

1. **Setup Vercel Blob Storage:**
   ```bash
   # Install Vercel CLI if not already installed
   npm i -g vercel
   
   # Link your project to Vercel
   vercel link
   
   # Add blob storage to your project
   vercel blob create
   ```

2. **Configure Environment Variable:**
   ```bash
   # In your .env file or Vercel dashboard
   BLOB_READ_WRITE_TOKEN=vercel_blob_rw_xxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Features:**
   - ✅ Automatic file uploads to Vercel Blob Storage
   - ✅ Direct CDN-served images (fast loading)
   - ✅ Automatic cleanup when posts/profile pictures are deleted
   - ✅ Supports JPEG, PNG, GIF, WebP image formats
   - ✅ Scalable for production use

**Option 2: Local File Storage (Development Fallback)**
When `BLOB_READ_WRITE_TOKEN` is not configured, the app falls back to local file storage in the `userUpload` directory. This is suitable for development but not recommended for production deployments.

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
