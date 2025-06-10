# app.py
# always use file name top of the code
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sys
import os

# Add the current directory to Python path for Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    get_posts,
    create_new_post,
    update_profile,
    init_db,
    delete_post,
    remove_profile_picture,
    get_user_by_username,
    get_user_by_id,
    db,
    init_app,
    User as DBUser,
    create_user,
    update_profile_picture,
)
import os
import datetime
from dotenv import load_dotenv
import re  # Add this at the top with other imports
import random
import string

load_dotenv()

now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your-secret-key-here")
app.config["UPLOAD_FOLDER"] = "userUpload"
UPLOAD_FOLDER = "userUpload"

# Initialize database with app
init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(UserMixin):
    def __init__(
        self,
        user_id,
        username,
        password,
        profile_picture,
        firstName="",
        lastName="",
        bio="",
        location="",
    ):
        self.id = user_id
        self.username = username
        self.password = password
        self.profile_picture = profile_picture
        self.firstName = firstName
        self.lastName = lastName
        self.bio = bio
        self.location = location


@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)
    
    if user_data:
        return User(
            user_data.id,
            user_data.username,
            user_data.password,
            user_data.profile_picture,
            user_data.firstName,
            user_data.lastName,
            user_data.bio,
            user_data.location,
        )
    return None


def is_valid_username(username):
    """Check if username contains only letters and numbers without spaces"""
    return bool(re.match("^[a-zA-Z0-9]+$", username))


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_data = get_user_by_username(username)

        if user_data and check_password_hash(user_data.password, password):
            # Include all user fields when creating User object
            user = User(
                user_data.id,
                user_data.username,
                user_data.password,
                user_data.profile_picture,
                user_data.firstName,
                user_data.lastName,
                user_data.bio,
                user_data.location,
            )
            login_user(user)
            return redirect(url_for("feed"))
        else:
            flash("Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/profile/<username>")  # Changed from <int:user_id>
@login_required
def profile(username):  # Changed parameter
    user_data = get_user_by_username(username)

    if user_data:
        profile_user = User(
            user_data.id,
            user_data.username,
            user_data.password,
            user_data.profile_picture,
            user_data.firstName,
            user_data.lastName,
            user_data.bio,
            user_data.location,
        )

        posts = get_posts(profile_user.id)
        is_owner = current_user.username == profile_user.username  # Changed comparison

        return render_template(
            "profile.html",
            user=profile_user,
            current_user=current_user,
            posts=posts,
            is_owner=is_owner,
            UPLOAD_FOLDER=UPLOAD_FOLDER,
            # post_id=posts,  # Pass post_id to template
        )
    else:
        flash("User not found.")
        return redirect(url_for("index"))


@app.route("/delete_post_route/<int:post_id>", methods=["POST"])
@login_required
def delete_post_function(post_id):
    try:
        delete_post(post_id)
        flash("Post deleted successfully.")
    except Exception as e:
        flash(f"An error occurred while deleting the post: {str(e)}")
    return redirect(url_for("profile", username=current_user.username))


@app.route("/delete_profile_picture", methods=["GET", "POST"])
@login_required
def delete_profile_picture():
    remove_profile_picture(current_user.id)
    return render_template("edit_profile.html", user=current_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not is_valid_username(username):
            flash("Username can only contain letters and numbers without spaces")
            return render_template("register.html")

        if create_user(username, password):
            flash("Registration successful! Please log in.")
            return redirect(url_for("login"))
        else:
            flash("Username already exists. Please choose a different one.")
    return render_template("register.html")


@app.route("/userUpload/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        try:
            content = request.form.get("content")
            image = request.files.get("image")

            if not content:
                flash("Post content cannot be empty")
                return redirect(url_for("create_post"))

            image_path = None
            if image:
                length = 8
                random_string = "".join(
                    random.choices(string.ascii_letters + string.digits, k=length)
                )
                filename = secure_filename(
                    f"post_{current_user.id}_{timestamp}_{random_string}.jpg"
                )
                try:
                    image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    image_path = f"/userUpload/{filename}"
                except Exception as e:
                    app.logger.error(f"Error saving image: {str(e)}")
                    flash("Error uploading image, post created without image")

            create_new_post(current_user.id, content, image_path)
            flash("Post created successfully!")
            return redirect(
                url_for("profile", username=current_user.username)
            )  # Changed to username

        except Exception as e:
            app.logger.error(f"Error creating post: {str(e)}")
            flash("An error occurred while creating the post. Please try again.")
            return redirect(url_for("create_post"))

    return render_template("create_post.html")


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        changeProfilePicture = request.files.get("profile_picture")
        changeUsername = request.form.get("username")
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        bio = request.form.get("bio")
        location = request.form.get("location")

        if changeProfilePicture:
            length = 8
            random_string = "".join(
                random.choices(string.ascii_letters + string.digits, k=length)
            )
            filename = secure_filename(f"profile_{current_user.id}_{random_string}.jpg")

            changeProfilePicture.save(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )
            image_path = f"/userUpload/{filename}"
            
            update_profile_picture(current_user.id, filename)
            create_new_post(current_user.id, "Updated profile picture!", image_path)

            flash("Profile picture updated!")

        if not is_valid_username(changeUsername):
            flash("Username can only contain letters and numbers without spaces")
            return render_template(
                "edit_profile.html", user=current_user, UPLOAD_FOLDER=UPLOAD_FOLDER
            )

        update_profile(
            current_user.id, changeUsername, firstName, lastName, bio, location
        )
        flash("Profile updated successfully!")
        return redirect(
            url_for("profile", username=changeUsername)
        )  # Changed to username

    return render_template(
        "edit_profile.html",
        user=current_user,
        UPLOAD_FOLDER=UPLOAD_FOLDER,
        firstName="",
        lastName="",
    )


@app.route("/feed", methods=["GET", "POST"])  # Add POST method
@login_required
def feed():
    try:
        if request.method == "POST":
            content = request.form.get("content")
            image = request.files.get("image")

            if not content:
                flash("Post content cannot be empty")
                return redirect(url_for("feed"))

            image_path = None
            if image:

                filename = secure_filename(
                    f"post_{current_user.id}_{timestamp}_{Math.random}.jpg"
                )
                try:
                    image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    image_path = f"/userUpload/{filename}"
                except Exception as e:
                    app.logger.error(f"Error saving image: {str(e)}")
                    flash("Error uploading image, post created without image")

            create_new_post(current_user.id, content, image_path)
            flash("Post created successfully!")
            return redirect(url_for("feed"))

        posts = get_posts()
        return render_template(
            "feed.html",
            posts=posts,
            UPLOAD_FOLDER=UPLOAD_FOLDER,
            current_user=current_user,
        )
    except Exception as e:
        flash("An error occurred while retrieving posts.")
        posts = []
        return render_template(
            "feed.html",
            posts=posts,
            UPLOAD_FOLDER=UPLOAD_FOLDER,
            current_user=current_user,
        )


# add port

if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    port = int(os.getenv("PORT", 5000))

    if env == "development":
        # Development settings
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        # Production settings - use Waitress
        from waitress import serve

        serve(app, host="0.0.0.0", port=port)

