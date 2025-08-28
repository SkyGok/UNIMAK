import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from helpers import apology, login_required, lookup, get_translations

# Configure application
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/..
db_path = os.path.join(BASE_DIR, "files", "unimak.db")

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to database
db = SQL("sqlite:///files/unimak.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# -------------------- HOME --------------------
@app.route("/", methods=["GET"])
@login_required
def index():
    """Show only project problem reports on main page"""
    rows = db.execute("""
        SELECT pr.df_number, p.project_number, p.manager_id, m.manager_name,
               pr.reason, pr.description, pr.photos_id, pr.record_date
        FROM problems pr
        JOIN projects p ON pr.project_number = p.id
        JOIN managers m ON p.manager_id = m.id
        ORDER BY pr.record_date DESC
    """)
    t = get_translations()
    return render_template("home.html", data=rows, t=t)


# -------------------- LOGIN --------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        session["user_id"] = rows[0]["id"]
        session["language"] = rows[0].get("language", "en")
        return redirect("/")
    else:
        return render_template("login.html")


# -------------------- LOGOUT --------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -------------------- REGISTER --------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return apology("Please fill all fields", 400)
        if password != confirmation:
            return apology("Passwords do not match", 400)

        if db.execute("SELECT * FROM users WHERE username = ?", username):
            return apology("Username already taken", 400)

        hash_pw = generate_password_hash(password)
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", username, hash_pw)
        return redirect("/login")
    else:
        return render_template("register.html")


# -------------------- UPLOAD PROBLEM --------------------
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        project_id = request.form.get("project_number")
        reason = request.form.get("reason")
        description = request.form.get("description")
        photos = request.files.getlist("photos")

        timestamp = datetime.now().strftime("%d%m%y%H%M%S")
        df_number = f"df_{timestamp}"
        folder_name = f"{df_number}_{project_id}"
        base_dir = os.path.join(os.path.dirname(__file__), "files/uploads", folder_name)
        pictures_dir = os.path.join(base_dir, "pictures")
        os.makedirs(pictures_dir, exist_ok=True)

        photo_filenames = []
        for idx, photo in enumerate(photos, start=1):
            if photo and photo.filename:
                filename = secure_filename(f"{folder_name}_{idx}.jpg")
                photo.save(os.path.join(pictures_dir, filename))
                photo_filenames.append(filename)

        # Save description.txt
        description_file = os.path.join(base_dir, f"{folder_name}.txt")
        with open(description_file, "w", encoding="utf-8") as f:
            f.write(f"User ID: {session['user_id']}\n")
            f.write(f"Project ID: {project_id}\n")
            f.write(f"DF Number: {df_number}\n")
            f.write(f"Reason: {reason}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Photos: {', '.join(photo_filenames)}\n")
            f.write(f"Timestamp: {timestamp}\n")

        # Insert into problems table
        db.execute("""
            INSERT INTO problems (project_number, df_number, reason, description, photos_id)
            VALUES (?, ?, ?, ?, ?)
        """, project_id, df_number, reason, description, ",".join(photo_filenames))

        flash("Problem reported successfully!", "success")
        return redirect("/")

    projects = db.execute("SELECT id, project_number FROM projects")
    reasons = [
        {"key": "reason.missing_components", "default": "Eksik Malzeme"},
        {"key": "reason.wrong_part", "default": "Uygunsuz Malzeme"},
        {"key": "reason.damaged_materials", "default": "Arızalı-Malzeme"},
        {"key": "reason.programming_issue", "default": "Otomasyon-Yazılım"},
        {"key": "reason.design_issue", "default": "Hatalı Proje"}
    ]
    department = [
        {"key": "department.sales", "default": "Sales"},
        {"key": "department.design", "default": "Design"},
        {"key": "department.method", "default": "Method"},
        {"key": "department.purchase", "default": "Purchase"},
        {"key": "department.manufacturing", "default": "Manufacturing"},
        {"key": "department.warehouse", "default": "Warehouse"},
        {"key": "department.quality", "default": "Quality"},
        {"key": "department.shipment", "default": "Shipment"},
        {"key": "department.automation", "default": "Automation"},
        {"key": "department.electronics", "default": "Electronics"},
        {"key": "department.international_assembly_electronics", "default": "International Assembly Electronics"},
        {"key": "department.international_assembly_mechanics", "default": "International Assembly Mechanics"}
    ]
    action = [
        {"key": "action.1", "default": "Send Parts"},
        {"key": "action.2", "default": "Fix On-spot"},
        {"key": "action.3", "default": "Customer Support"},
        {"key": "action.4", "default": "Software Revision"}
    ]
    priority = [
        {"key": "priority.low", "default": "Low"},
        {"key": "priority.normal", "default": "Normal"},
        {"key": "priority.high", "default": "High"}
    ]
    t = get_translations()
    return render_template("upload.html", projects=projects, reasons=reasons,priority=priority, action=action, department=department, t=t)


# -------------------- INFO --------------------
@app.route("/info", methods=["GET"])
@login_required
def info():
    rows = db.execute("""
        SELECT m.manager_name, p.project_number, pr.df_number, pr.reason, pr.description, pr.photos_id
        FROM managers m
        LEFT JOIN projects p ON p.manager_id = m.id
        LEFT JOIN problems pr ON pr.project_number = p.id
        ORDER BY m.manager_name, p.project_number
    """)

    data = {}
    for row in rows:
        manager = row["manager_name"]
        if manager not in data:
            data[manager] = []
        if row["project_number"]:
            data[manager].append({
                "project_number": row["project_number"],
                "df_number": row.get("df_number"),
                "reason": row.get("reason"),
                "description": row.get("description"),
                "photos": row.get("photos_id").split(",") if row.get("photos_id") else []
            })

    t = get_translations()
    return render_template("info.html", data=data, t=t)


# -------------------- HISTORY --------------------
@app.route("/history", methods=["GET"])
@login_required
def history():
    rows = db.execute("""
        SELECT pr.df_number, p.project_number, m.manager_name, pr.reason, pr.description, pr.photos_id, pr.record_date
        FROM problems pr
        JOIN projects p ON pr.project_number = p.id
        JOIN managers m ON p.manager_id = m.id
        ORDER BY pr.record_date DESC
    """)
    t = get_translations()
    return render_template("history.html", data=rows, t=t)


# -------------------- ADMIN --------------------
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    t = get_translations()
    return render_template("admin.html", t=t)


# -------------------- RUN APP --------------------
if __name__ == "__main__":
    app.run(debug=True)
