import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session,url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from helpers import apology, login_required, lookup, get_translations
from flask import send_from_directory
from flask import request, jsonify
from dropdowns import reasons, department, action, priority
import requests
from collections import defaultdict
# ------------------------
# Configure application
# ------------------------
app = Flask(__name__)



@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    query = data.get("query")

    # Call the NLP Cloud Summarization API
    api_url = "https://api.nlpcloud.io/v1/bart-large-cnn/summarize"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json",
    }
    payload = {
        "text": query,
    }
    response = requests.post(api_url, headers=headers, json=payload)
    summary = response.json().get("summary", "Sorry, I couldn't generate a summary.")

    return jsonify({"summary": summary})



@app.route('/static/files/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.root_path, '/static/files/uploads'), filename)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/..
db_path = os.path.join(BASE_DIR, "/static/files", "unimak.db")

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to database
db = SQL("sqlite:///static/files/unimak.db")

# ------------------------
# After request: prevent caching
# ------------------------
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# -------------------- HOME --------------------
@app.route("/", methods=["GET"])
@login_required
def index():
    """Show latest project problem reports on main page"""
    rows = db.execute("""
        SELECT pr.id AS problem_id,
               p.project_number,
               p.project_name,
               m.manager_name,
               pr.created_at AS record_date,
               u.username AS record_opened_by,
               g.group_name
        FROM problems pr
        JOIN projects p ON pr.project_id = p.id
        JOIN managers m ON p.manager_id = m.id
        JOIN users u ON pr.user_id = u.id
        JOIN groups g ON pr.group_id = g.id
        ORDER BY pr.created_at DESC
    """)

    # Example: add placeholders for missing columns used in template
    for row in rows:
        row["df_number"] = f"DF_{row['problem_id']}"  # generate a DF number
        row["reason"] = "N/A"  # placeholder, you can link to problem_components later
        row["description"] = "-"  # placeholder
        row["photos_id"] = None  # no photos for now
        row["photo_urls"] = []
        row["status"] = "Pending"  # default
        row["reason_display"] = row["reason"]

    t = get_translations()
    return render_template("home.html",
                           data=rows,
                           t=t,
                           reasons=[],  # define your reason options here
                           priority=[],  # define your priority options
                           action=[]  # define your action options
                           )


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
    # Get all managers
    managers = db.execute("SELECT id, manager_name, manager_mail FROM managers")

    # Get all customers
    customers = db.execute("SELECT id, customer_name, customer_country FROM customers")

    # Get all projects
    projects = db.execute("""
        SELECT p.id, p.project_number, p.project_name, p.quantity,
               m.manager_name, c.customer_name
        FROM projects p
        JOIN managers m ON p.manager_id = m.id
        JOIN customers c ON p.customer_id = c.id
    """)

    # Get groups with engineer info (to allow problem linking)
    groups = db.execute("""
        SELECT g.id, g.project_id, e.engineer_name,
            g.group_number, g.group_name
        FROM groups g
        JOIN engineers e ON g.engineer_id = e.id
    """)


    # Get components info (to allow problem linking)
    components = db.execute("""
        SELECT
            c.id,
            c.group_id,            -- needed for filtering
            c.component_no,
            c.component_name,
            c.unit_quantity,
            c.total_quantity
        FROM components c;
    """)


    data = {
        "managers": managers,
        "customers": customers,
        "projects": projects,
        "groups": groups,
        "components": components,
    }

    if request.method == "POST":
        project_id = request.form.get("project_id")
        group_id = request.form.get("group_id")
        photos = request.files.getlist("photos")
        component_ids = request.form.getlist("component_id[]")  # list of selected components
        reasons = request.form.getlist("reason[]")
        departments = request.form.getlist("department[]")
        actions = request.form.getlist("action[]")
        priorities = request.form.getlist("priority[]")
        descriptions = request.form.getlist("description[]")

        for i in range(len(component_ids)):
            db.execute("""
                INSERT INTO problem_components 
                (problem_id, component_id, reason, department, action, priority, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, problem_id, component_ids[i], reasons[i], departments[i], actions[i], priorities[i], descriptions[i])


        timestamp = datetime.now().strftime("%d%m%y%H%M%S")
        df_number = f"df_{timestamp}"

        components_data = []

        

        folder_name = df_number
        # ✅ Corrected: no leading slash, path relative to project
        base_dir = os.path.join(os.path.dirname(__file__), "static", "files", "uploads", folder_name)
        pictures_dir = os.path.join(base_dir, "pictures")
        os.makedirs(pictures_dir, exist_ok=True)

        photo_filenames = []
        for idx, photo in enumerate(photos, start=1):
            if photo and photo.filename:
                filename = secure_filename(f"{folder_name}_{idx}.jpg")
                photo.save(os.path.join(pictures_dir, filename))
                photo_filenames.append(filename)

        # print("DEBUG:", project_id, group_id, df_number, session["user_id"], reason, description, photo_filenames)

        # 1. Insert the main problem
        db.execute("""
            INSERT INTO problems (project_id, group_id, user_id)
            VALUES (?, ?, ?)
        """, project_id, group_id, session["user_id"])

        # Get the ID of the newly created problem
        problem_id = db.execute("SELECT last_insert_rowid() AS id")[0]["id"]

        # 2. Insert the detailed component info
        db.execute("""
            INSERT INTO problem_components 
            (problem_id, component_id, reason, department, action, priority, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, problem_id, component_ids, reasons, department, action, priority, descriptions)

        # 3. (Optional) If you still need problem_steps
        db.execute("""
            INSERT INTO problem_steps (problem_id, step_number, df_filename)
            VALUES (?, ?, ?)
        """, problem_id, 1, f"{df_number}.xlsx")


        flash("Problem reported successfully!", "success")
        return redirect("/")

    t = get_translations()
    return render_template("admin.html",  
                        data=data,
                        reasons = reasons,
                        priority = priority,
                        department = department,
                        action = action,
                        t=t)

# -------------------- INFO --------------------
@app.route("/info", methods=["GET"])
@login_required
def info():
    # Single query to get managers -> projects -> problems (may produce repeated project rows when multiple problems exist)
    rows = db.execute("""
        SELECT
            m.id AS manager_id,
            m.manager_name,
            p.id AS project_id,
            p.project_number,
            p.quantity,
            pr.id AS problem_id,
            pr.df_number,
            pr.reason,
            pr.description AS problem_description,
            pr.photos_id,
            pr.status,
            pr.record_date
        FROM managers m
        LEFT JOIN projects p ON p.manager_id = m.id
        LEFT JOIN problems pr ON pr.project_id = p.id
        ORDER BY m.manager_name, p.project_number, pr.record_date DESC
    """)


    # Build nested structure: { manager_name: [ { project }, { project }, ... ] }
    data = {}
    # helper map to track added projects per manager for O(1) lookup
    project_index = {}

    for row in rows:
        manager = row["manager_name"] or "Unassigned"

        if manager not in data:
            data[manager] = []
            project_index[manager] = {}

        project_id = row["project_id"]

        # If there is a project (project_id can be None when manager has no projects)
        if project_id:
            # create project entry only once per manager
            if project_id not in project_index[manager]:
                project_obj = {
                    "id": project_id,
                    "project_number": row["project_number"],
                    "quantity": row.get("quantity"),
                    "machine_type": row.get("machine_type"),
                    "machine_top_group": row.get("machine_top_group"),
                    # placeholder for project-level description (if you add one later)
                    "description": row.get("project_description") if "project_description" in row.keys() else None,
                    "problems": []
                }
                project_index[manager][project_id] = project_obj
                data[manager].append(project_obj)

            # append problem if exists
            if row["problem_id"]:
                photos = []
                if row["photos_id"]:
                    # photos stored as comma-separated filenames
                    photos = [p.strip() for p in row["photos_id"].split(",") if p.strip()]

                problem_obj = {
                    "id": row["problem_id"],
                    "df_number": row.get("df_number"),
                    "reason": row.get("reason"),
                    "description": row.get("problem_description"),
                    "photos": photos,
                    "status": row.get("status"),
                    "record_date": row.get("record_date")
                }
                project_index[manager][project_id]["problems"].append(problem_obj)

    # ensure managers with no projects still show up (data[manager] would be empty list)
    t = get_translations() if callable(globals().get("get_translations", None)) else {}

    return render_template("info.html", data=data, t=t)

# -------------------- HISTORY --------------------
@app.route("/history", methods=["GET"])
@login_required
def history():
    rows = db.execute("""
        SELECT ps.df_filename, p.project_number, m.manager_name, pr.reason, pr.description, pr.photos_id, ps.created_at
        FROM problem_steps ps
        JOIN problems pr ON ps.problem_id = pr.id
        JOIN projects p ON pr.project_id = p.id
        JOIN managers m ON p.manager_id = m.id
        ORDER BY ps.created_at DESC
    """)
    t = get_translations()
    return render_template("history.html", data=rows, t=t)

# -------------------- ADMIN --------------------
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    problems = db.execute("""
        SELECT 
            p.id AS problem_id,
            p.created_at,
            pj.project_number,
            pj.project_name,
            m.manager_name,
            c.customer_name,
            g.group_name,
            g.group_number,
            e.engineer_name,
            pc.id AS pc_id,
            comp.component_name,
            comp.component_no,
            pc.reason,
            pc.description,
            pc.priority,
            pc.action,
            pc.department,
            ps.df_filename
        FROM problems p
        JOIN projects pj ON pj.id = p.project_id
        JOIN managers m ON pj.manager_id = m.id
        JOIN customers c ON pj.customer_id = c.id
        JOIN groups g ON g.id = p.group_id
        JOIN engineers e ON g.engineer_id = e.id
        LEFT JOIN problem_components pc ON pc.problem_id = p.id
        LEFT JOIN components comp ON comp.id = pc.component_id
        LEFT JOIN problem_steps ps ON ps.problem_id = p.id
        ORDER BY p.created_at DESC
    """)

    problem_dict = defaultdict(lambda: {"components": [], "photos": []})

    for row in problems:
        prob = problem_dict[row["problem_id"]]
        prob.update({
            "problem_id": row["problem_id"],
            "created_at": row["created_at"],
            "project_number": row["project_number"],
            "project_name": row["project_name"],
            "manager_name": row["manager_name"],
            "customer_name": row["customer_name"],
            "group_name": row["group_name"],
            "group_number": row["group_number"],
            "engineer_name": row["engineer_name"],
            "df_filename": row["df_filename"]
        })
        if row["pc_id"]:
            prob["components"].append({
                "component_name": row["component_name"],
                "component_no": row["component_no"],
                "reason": row["reason"],
                "description": row["description"],
                "priority": row["priority"],
                "action": row["action"],
                "department": row["department"]
            })

    # Attach photos from filesystem
    base_path = os.path.join(app.root_path, "static/files/uploads")
    for prob in problem_dict.values():
        df_prefix = prob["df_filename"].split(".")[0] if prob["df_filename"] else None
        if df_prefix:
            pictures_dir = os.path.join(base_path, df_prefix, "pictures")
            if os.path.exists(pictures_dir):
                prob["photos"] = os.listdir(pictures_dir)

    data = list(problem_dict.values())
    return render_template("admin.html", data=data)


# -------------------- RUN APP --------------------
if __name__ == "__main__":
    app.run(debug=True)
