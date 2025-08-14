import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

import sqlite3

from helpers import apology, login_required, lookup, get_translations


# Configure application
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/..
db_path = os.path.join(BASE_DIR, "files", "unimak.db")

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure Monit database
db = SQL("sqlite:///files/unimak.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    rows = db.execute("""
        SELECT 
            p.project_number,
            m.manager_name AS project_manager,
            p.reason,
            p.description
        FROM projects p
        JOIN managers m ON p.manager_id = m.id
    """)

    data = []
    for row in rows:
        data.append({
            "project": row["project_number"],
            "manager": row["project_manager"],
            "reason": row["reason"],
            "description": row["description"]
        })
    t = get_translations()
    return render_template("home.html", data=data, t=t)





@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400) 

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password_hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must confirm password", 400)
        elif password != confirmation:
            return apology("passwords do not match", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return apology("username already taken", 400)

        hash_pw = generate_password_hash(password)
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", username, hash_pw)

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Uploading page"""
    if request.method == "POST":
        project_number = request.form.get("project_number")
        reason = request.form.get("reason")
        description = request.form.get("description")
        photos = request.files.getlist("photos")

        # Step 1: Create a unique folder based on project_number and timestamp
        timestamp = datetime.now().strftime("%d%m%y%H%M%S")  # e.g., 1308250939
        folder_name = f"{project_number}_{timestamp}"
        base_dir = os.path.join(os.path.dirname(__file__), "files/uploads", folder_name)
        pictures_dir = os.path.join(base_dir, "pictures")

        os.makedirs(pictures_dir, exist_ok=True)  # creates base_dir/pictures

        # Step 2: Save photos inside pictures_dir
        for idx, photo in enumerate(photos, start=1):
            if photo and photo.filename:
                filename = secure_filename(f"{folder_name}_{idx}.jpg")
                photo.save(os.path.join(pictures_dir, filename))

        # Step 3: Create description.txt inside base_dir
        description_file = os.path.join(base_dir, f"{folder_name}.txt")
        with open(description_file, "w", encoding="utf-8") as f:
            f.write(f"User ID: {session['user_id']}\n")
            f.write(f"Project Number: {project_number}\n")
            f.write(f"Reason: {reason}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Timestamp: {timestamp}\n")

        # Step 4: Insert record into DB (if needed)
        # db.execute("INSERT INTO projects (...) VALUES (...)", ...)

        flash("Project issue reported successfully!", "success")
        return redirect("/")

    # GET request
    projects = db.execute("SELECT id, project_number FROM projects")
    reasons = ["Incorrect installation", "Damaged materials", "Missing components", "Design issue", "Other"]
    return render_template("upload.html", projects=projects, reasons=reasons)

@app.route("/info", methods=["GET", "POST"])
@login_required
def info():
     # Query managers and their projects
    rows = db.execute("""
        SELECT m.id AS manager_id, m.manager_name, p.project_number
        FROM managers m
        LEFT JOIN projects p ON p.manager_id = m.id
        ORDER BY m.manager_name
    """)

    # Transform rows into a dictionary: {manager_name: [projects]}
    data = {}
    for row in rows:
        manager = row["manager_name"]
        project = row["project_number"]
        if manager not in data:
            data[manager] = []
        if project:
            data[manager].append(project)

    return render_template("info.html", data=data)
    

@app.route("/history", methods=["GET"])
@login_required
def history():
    rows = db.execute("""
        SELECT 
            p.project_number, 
            m.manager_name, 
            p.reason, 
            p.description, 
            p.record_date
        FROM projects p
        JOIN managers m ON p.manager_id = m.id
        ORDER BY p.record_date DESC
    """)
    t = get_translations()
    return render_template("history.html", data=rows, t=t)

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        # Get selected language from form
        language = request.form.get("language")
        
        # Save to session (quick method)
        session["language"] = language

        # Optionally, save to database for persistent preference
        db.execute("UPDATE users SET language = ? WHERE id = ?", language, session["user_id"])

        flash("Language updated successfully!", "success")
        return redirect("/settings")

    # GET request
    user_language = session.get("language", "en")  # default to English
    t = get_translations()
    return render_template("settings.html", user_language=user_language, t=t)

if __name__ == "__main__":
    app.run(debug=True)
