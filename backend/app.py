import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

import sqlite3

from helpers import apology, login_required, lookup

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
    rows = db.execute(
        "SELECT project_number, project_manager, reason, description FROM projects"
    )

    # If you still want to run lookup() for each:
    data = []
    for row in rows:
        data.append({
            "project": lookup(row["project_number"]) if lookup else row["project_number"],
            "manager": lookup(row["project_manager"]) if lookup else row["project_manager"],
            "reason": row["reason"],
            "description": row["description"]
        })

    return render_template("home.html", data=data)




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
    return render_template("upload.html")

@app.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    """Show projects"""
    return render_template("projects.html")
    

@app.route("/history", methods=["GET"])
@login_required
def history():
    """Show portfolio of stocks"""
    return render_template("history.html")

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Show portfolio of stocks"""
    return render_template("settings.html")



if __name__ == "__main__":
    app.run(debug=True)
