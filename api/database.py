# database.py
# always use file name top of the code
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from sqlalchemy import text

load_dotenv()

db = SQLAlchemy()

# Database Models
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    profile_picture = db.Column(db.String(255), default='placeholder.jpg')
    bio = db.Column(db.Text, default='')
    location = db.Column(db.String(255), default='')
    
    # Relationship with posts
    posts = db.relationship('Post', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Post {self.id}>'


def init_app(app):
    """Initialize the database with the Flask app."""
    # Configure PostgreSQL database URL with SQLite fallback for development
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Detect if we're running in Vercel/serverless environment
        is_vercel = os.getenv('VERCEL') == '1' or os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None
        
        # Handle postgres:// URLs and choose driver based on environment
        if database_url.startswith('postgres://'):
            if is_vercel:
                # Use pg8000 for Vercel/serverless environments for better compatibility
                database_url = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
                driver_name = "pg8000"
            else:
                # Use psycopg2 for local/traditional environments
                database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
                driver_name = "psycopg2"
        elif database_url.startswith('postgresql://'):
            if is_vercel:
                # Use pg8000 for Vercel/serverless environments
                if '+pg8000' not in database_url:
                    database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
                driver_name = "pg8000"
            else:
                # Use psycopg2 for local/traditional environments
                if '+psycopg2' not in database_url and '+pg8000' not in database_url:
                    database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
                driver_name = "psycopg2" if '+psycopg2' in database_url else "pg8000"
        
        # Handle SSL configuration based on driver
        if driver_name == "pg8000":
            # pg8000 uses ssl_context instead of sslmode
            if 'sslmode=require' in database_url:
                database_url = database_url.replace('?sslmode=require', '')
                database_url = database_url.replace('&sslmode=require', '')
                # For pg8000, we need to remove SSL parameters as it will use default SSL
                # The driver will automatically use SSL if the server requires it
        else:
            # psycopg2 natively supports sslmode parameter, so we keep it as is
            pass
        
        print(f"Using PostgreSQL database with {driver_name} driver ({'Vercel/serverless' if is_vercel else 'local'} environment)")
    else:
        # Fallback to SQLite for development if PostgreSQL is not configured
        database_url = 'sqlite:///facebook_clone.db'
        print("Warning: Using SQLite fallback. Configure DATABASE_URL for PostgreSQL.")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # Test the connection first
            db.engine.connect()
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Database connection error: {e}")
            if 'sslmode=require' in str(database_url) or 'SSL' in str(e):
                print("SSL connection failed. Check your DATABASE_URL SSL configuration.")
                print("Make sure your DATABASE_URL includes '?sslmode=require' or other appropriate SSL parameters.")
            
            # Fallback to SQLite if PostgreSQL connection fails
            print("Switching to SQLite fallback...")
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facebook_clone.db'
            # Re-initialize with SQLite
            try:
                db.create_all()
                print("Successfully switched to SQLite fallback.")
            except Exception as sqlite_error:
                print(f"SQLite fallback also failed: {sqlite_error}")
                raise sqlite_error


def init_db():
    """Initialize the database tables."""
    db.create_all()


def create_new_post(user_id, content, image=None):
    """Create a new post"""
    try:
        post = Post(
            user_id=user_id,
            content=content,
            image=image
        )
        db.session.add(post)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e


def delete_post(post_id):
    """Delete a post by its ID."""
    try:
        post = Post.query.get(post_id)
        if post:
            db.session.delete(post)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        raise e


def remove_profile_picture(user_id):
    """Remove the user's profile picture."""
    try:
        user = User.query.get(user_id)
        if user:
            user.profile_picture = 'placeholder.jpg'
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        raise e


def create_user(username, password, firstName=None, lastName=None):
    """Create a new user in the database."""
    try:
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        user = User(
            username=username,
            password=hashed_password,
            firstName=firstName,
            lastName=lastName
        )
        db.session.add(user)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False  # Username already exists or other error


def get_user_by_username(username):
    """Retrieve a user by their username."""
    return User.query.filter_by(username=username).first()


def get_user_by_id(user_id):
    """Retrieve a user by their ID."""
    return User.query.get(user_id)


def update_profile(user_id, username, firstName, lastName, bio, location):
    """Update user profile details"""
    try:
        user = User.query.get(user_id)
        if user:
            user.username = username
            user.firstName = firstName
            user.lastName = lastName
            user.bio = bio
            user.location = location
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        raise e


def get_posts(user_id=None):
    """Get posts for a specific user or all posts"""
    if user_id:
        # Get posts for a specific user with user information
        posts = db.session.query(Post, User).join(User).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()
    else:
        # Get all posts with user information
        posts = db.session.query(Post, User).join(User).order_by(Post.created_at.desc()).all()
    
    # Convert to a format similar to the original SQLite row factory
    result = []
    for post, user in posts:
        post_dict = {
            'id': post.id,
            'user_id': post.user_id,
            'content': post.content,
            'image': post.image,
            'created_at': post.created_at,
            'username': user.username,
            'profile_picture': user.profile_picture
        }
        result.append(post_dict)
    
    return result


def update_profile_picture(user_id, filename):
    """Update the user's profile picture."""
    try:
        user = User.query.get(user_id)
        if user:
            user.profile_picture = filename
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        raise e
