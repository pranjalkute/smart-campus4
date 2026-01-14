from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "hackathon_secret"
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------- LOGIN DATA --------
students = {
    "student1@gmail.com": "1234",
    "student2@gmail.com": "abcd"
}

admin = {
    "admin@gmail.com": "admin123"
}

# -------- DATABASE --------
def get_db():
    return sqlite3.connect("database.db")

# -------- AI TEXT --------
def detect_category(text):
    text = text.lower()
    if any(w in text for w in ["light", "fan", "power"]):
        return "Electrical"
    elif any(w in text for w in ["water", "pipe", "toilet"]):
        return "Plumbing"
    elif any(w in text for w in ["road", "building"]):
        return "Infrastructure"
    return "General"

# -------- AI IMAGE --------
def detect_image_category(name):
    if not name:
        return None
    name = name.lower()
    if "light" in name:
        return "Electrical"
    if "water" in name:
        return "Plumbing"
    if "road" in name:
        return "Infrastructure"
    return None

def confidence_score(cat):
    return {"Electrical": 90, "Plumbing": 85, "Infrastructure": 80}.get(cat, 60)

# -------- LOGIN --------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if role == "student":
            if email in students and students[email] == password:
                session["role"] = "student"
                return redirect("/report")
            return render_template("login.html", error="Invalid Student Login")

        if role == "admin":
            if email in admin and admin[email] == password:
                session["role"] = "admin"
                return redirect("/admin")
            return render_template("login.html", error="Invalid Admin Login")

    return render_template("login.html")

# -------- REPORT --------
@app.route("/report", methods=["GET","POST"])
def report():
    if session.get("role") != "student":
        return redirect("/")

    if request.method == "POST":
        issue = request.form["issue"]
        desc = request.form["description"]

        photo = request.files["photo"]
        filename = None
        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(UPLOAD_FOLDER, filename))

        text_cat = detect_category(issue + desc)
        img_cat = detect_image_category(filename)
        category = img_cat if img_cat else text_cat
        conf = confidence_score(category)

        conn = get_db()
        conn.execute(
            "INSERT INTO complaints VALUES(NULL,?,?,?,?,?,?)",
            (issue, desc, category, conf, filename, "Pending")
        )
        conn.commit()
        conn.close()

    return render_template("report.html")

# -------- DASHBOARD --------
@app.route("/dashboard")
def dashboard():
    conn = get_db()
    data = conn.execute("SELECT * FROM complaints").fetchall()
    conn.close()
    return render_template("dashboard.html", complaints=data)

# -------- ADMIN --------
@app.route("/admin")
def admin_panel():
    if session.get("role") != "admin":
        return redirect("/")
    conn = get_db()
    data = conn.execute("SELECT * FROM complaints").fetchall()
    conn.close()
    return render_template("admin.html", complaints=data)

@app.route("/update/<int:id>")
def update(id):
    conn = get_db()
    conn.execute("UPDATE complaints SET status='Solved' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

app.run(debug=True)