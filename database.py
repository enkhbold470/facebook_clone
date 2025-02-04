# database.py
# always use file name top of the code
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

# Set a default database name if environment variable is not found
DATABASE_NAME = os.getenv("DATABASE_NAME", "a.sqlite")


def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db():
    """Initialize the database with the required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the user table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            firstName TEXT,
            lastName TEXT,
            profile_picture TEXT DEFAULT 'placeholder.jpg',
            bio TEXT DEFAULT '',
            location TEXT DEFAULT ''
        )
    """
    )

    # Create posts table with global PST time for created_at
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            image TEXT,
            created_at TIMESTAMP DEFAULT (datetime('now', '-8 hours')),
            FOREIGN KEY(user_id) REFERENCES user(id)
        )
    """
    )

    conn.commit()
    conn.close()


def create_new_post(user_id, content, image=None):
    """Create a new post"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO posts (user_id, content, image)
        VALUES (?, ?, ?)
    """,
        (user_id, content, image),
    )

    conn.commit()
    conn.close()


def delete_post(post_id):
    """Delete a post by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()


def remove_profile_picture(user_id):
    """Remove the user's profile picture."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE user
        SET profile_picture = 'placeholder.jpg'
        WHERE id = ?
    """,
        (user_id,),
    )

    conn.commit()
    conn.close()


def create_user(username, password):
    """Create a new user in the database."""
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO user (username, password, firstName, lastName)
            VALUES (?, ?, ?, ?)
        """,
            (username, hashed_password),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

    return True


def get_user_by_username(username):
    """Retrieve a user by their username."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()

    conn.close()
    return user


def update_profile(user_id, username, firstName, lastName, bio, location):
    """Update user profile details"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE user
        SET username = ?, firstName = ?, lastName = ?, bio = ?, location = ?
        WHERE id = ?
    """,
        (username, firstName, lastName, bio, location, user_id),
    )

    conn.commit()
    conn.close()


def get_posts(user_id=None):
    """Get posts for a specific user or all posts"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if user_id:
        cursor.execute(
            """
            SELECT posts.*, user.username, user.profile_picture 
            FROM posts 
            JOIN user ON posts.user_id = user.id
            WHERE user_id = ?
            ORDER BY created_at DESC
        """,
            (user_id,),
        )
    else:
        cursor.execute(
            """
            SELECT posts.*, user.username, user.profile_picture 
            FROM posts 
            JOIN user ON posts.user_id = user.id
            ORDER BY created_at DESC
        """
        )

    posts = cursor.fetchall()
    conn.close()
    return posts


def update_profile_picture(user_id, filename):
    """Update the user's profile picture."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE user
        SET profile_picture = ?
        WHERE id = ?
    """,
        (filename, user_id),
    )

    conn.commit()
    conn.close()
