from flask import Flask, render_template, request, redirect, session, flash
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

db = SQL("sqlite:///edutrack.db")

db.execute("CREATE TABLE IF NOT EXISTS homework (id INTEGER PRIMARY KEY AUTOINCREMENT, class_name TEXT, subject TEXT, homework TEXT, date TEXT)")
db.execute("""CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, hash TEXT)""")
db.execute("""CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, class TEXT)""")
db.execute("""CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT, class_name TEXT, status INTEGER, date TEXT)""")
db.execute("""CREATE TABLE IF NOT EXISTS teachers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)""")
db.execute("""CREATE TABLE IF NOT EXISTS teacher_attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, teacher_name TEXT, status INTEGER, date TEXT)""")
db.execute("""CREATE TABLE IF NOT EXISTS notices (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL, date TEXT DEFAULT CURRENT_DATE, posted_by TEXT)""")
# Add this in app.py after your notices table creation
db.execute("""
CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                        due_date TEXT NOT NULL,
                            status TEXT DEFAULT 'Pending',
                                message TEXT
)
""")


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    homework = db.execute("SELECT * FROM homework")

    return render_template("index.html", school_name="DREAMLAND CHILD ACADEMY", address="Khalaigram, Salbari, Dhupguri, Jalpaiguri, 735210", start_time="10:30 AM", prayer_time="10:50 AM", juniors_ending_time="1:00 AM", seniors_ending_time="1:45 AM", Major_teacher="Tahera Banu jinnah", contact="7718684407", homework=homework)


@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "735":
            session["user_id"] = 1
            return redirect("/")

        else:

            return "wrong username or password"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/add_homework", methods=["GET", "POST"])
def add_homework():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        print("Submitted")

        class_name = request.form.get("class")

        subject = request.form.get("subject")

        homework = request.form.get("homework")

        date = request.form.get("date")

        db.execute("INSERT INTO homework (class_name, subject, homework, date) VALUES (?, ?, ?, ?)", class_name, subject, homework, date)

        return redirect("/")

    return render_template("add_homework.html")

@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        name = request.form.get("name")

        class_name = request.form.get("class")

        if not name or not class_name:

            return "please fill all fields"

        db.execute("INSERT INTO students (name, class) VALUES (?, ?)", name, class_name)

        return redirect("/add_student")

    students = db.execute("SELECT * FROM students")

    return render_template("add_stufent.html", students=students)

@app.route("/teacher_attendance", methods=["GET", "POST"])
def teacher_attendance():

    if "user_id" not in session:
        return redirect("/login")

    date = request.args.get("date")

    print("Date:", date)

    teachers = db.execute("SELECT * FROM teachers")

    if request.method == "POST":
        date = request.form.get("date")

        for teacher in teachers:
            teacher_name = teacher["name"]

            print("TEACHER NAME:", teacher_name)

            status = request.form.get(f"status_{teacher['name']}")

            print("STATUS:", status)

            if status is not None:

                db.execute("""DELETE FROM teacher_attendance WHERE teacher_name = ? AND date = ?""", teacher_name, date)

                print("Delete")

                db.execute("""INSERT INTO teacher_attendance  (teacher_name, status, date) VALUES (?, ?, ?)""", teacher_name, status, date)

                print(teacher_name, status)

        return redirect(f"/teacher_attendance?date={date}")

    attendance_rows = db.execute("SELECT teacher_name, status FROM teacher_attendance WHERE date = ?", date)

    attendance_data = {}

    for row in attendance_rows:
        attendance_data[row["teacher_name"]] = row["status"]

    history = db.execute("SELECT * FROM teacher_attendance ORDER BY date DESC")

    return render_template("teacher_attendance.html", teachers=teachers, history=history, date=date, attendance_data=attendance_data)

@app.route("/delete_teacher_attendance/<int:id>")
def delete_teacher_attendance(id):

    if "user_id" not in session:
        return redirect("/login")

    db.execute("DELETE FROM teacher_attendance WHERE id = ?", id)

    return redirect("/teacher_attendance")

@app.route("/add_teacher", methods=["GET", "POST"])
def add_teacher():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        name = request.form.get("name")

        if name:
            db.execute("INSERT INTO teachers (name) VALUES (?)", name)

        return redirect("/add_teacher")

    teachers = db.execute("SELECT * FROM teachers")

    return render_template("add_teacher.html", teachers=teachers)

@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    if "user_id" not in session:
        return redirect("/login")

    class_name = request.args.get("class")

    print("class_name:", class_name)

    date = request.args.get("date")

    print("Date:", date)

    students = []

    if class_name:
        students = db.execute("SELECT * FROM students WHERE class = ?", class_name)

    if request.method == "POST":

        print("FORM DATA:", request.form)

        class_name = request.form.get("class")

        date = request.form.get("date")

        students = db.execute("SELECT * FROM students WHERE class = ?", class_name)

        for student in students:

            student_name = student["name"]

            print("STUDENT NAME", student_name)

            status = request.form.get(f"status_{student['name']}")
            print("student:", student['name'], "status:", status)

            print("STATUS", status)

            if status is not None:

                db.execute("DELETE FROM attendance WHERE date = ? AND student_name = ?", date, student['name'])
                print("Delete")

                db.execute("INSERT INTO attendance (student_name, date, status, class_name) VALUES (?, ?, ?, ?)", student['name'], date, status, class_name)

                print(student_name, status)

        return redirect(f"/attendance?class={class_name}&date={date}")

    attendance_rows = db.execute("""SELECT student_name, status FROM attendance WHERE date = ? AND class_name = ?""", date, class_name)

    attendance_data = {}

    for row in attendance_rows:

       attendance_data[row["student_name"]] = row["status"]

    history = db.execute("SELECT * FROM attendance WHERE class_name = ? ORDER BY date DESC", class_name)

    return render_template("attendance.html", students=students, class_name=class_name, history=history, date=date, attendance_data=attendance_data)

@app.route("/delete_attendance/<int:id>")
def delete_attendance(id):

    if "user_id" not in session:
        return redirect("/login")

    db.execute("DELETE FROM attendance WHERE id = ?", id)

    return redirect("/attendance")

@app.route("/delete_teacher/<int:id>")
def delete_teacher(id):
    if "user_id" not in session:
        return redirect("/login")

    db.execute("DELETE FROM teachers WHERE id = ?", id)

    return redirect("/add_teacher")

@app.route("/delete_student/<int:id>")
def delete_student(id):
    if "user_id" not in session:
        return redirect("/login")

    db.execute("DELETE FROM students WHERE id = ?", id)

    return redirect("/add_student")

@app.route("/delete_homework/<int:id>")
def delete_homework(id):

    if "user_id" not in session:
        return redirect("/login")

    db.execute("DELETE FROM homework WHERE id = ?", id)

    return redirect("/")

@app.route("/notices", methods=["GET", "POST"])
def notices():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        if not title or not content:
            return "Title and content required"

        db.execute("INSERT INTO notices (title, content, posted_by) VALUES (?, ?, ?)", title, content, "Admin")

        return redirect("/notices")

    all_notices = db.execute("SELECT * FROM notices ORDER BY date DESC, id DESC")
    return render_template("notices.html", notices=all_notices)

@app.route("/delete_notice/<int:id>")
def delete_notice(id):

    if "user_id" not in session:
        return redirect("/login")

    db.execute("DELETE FROM notices WHERE id = ?", id)
    return redirect("/notices")

@app.route("/parent_notices")
def parent_notices():

    if "user_id" not in session:
        return redirect("/login")

    all_notices = db.execute("SELECT * FROM notices ORDER BY date DESC")
    return render_template("/parent_notices.html", notices=all_notices)

@app.route("/fees")
def fees():

        if "user_id" not in session:
            return redirect("/login")

        fees_list = db.execute("SELECT * FROM fees ORDER BY due_date DESC")
        return render_template("fees.html", fees_list=fees_list)

@app.route("/add_fee", methods=["GET", "POST"])
def add_fee():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        student_name = request.form.get("student_name")
        class_name = request.form.get("class_name")
        amount = request.form.get("amount")
        due_date = request.form.get("due_date")
        message = request.form.get("message")

        print("Form data:", student_name, class_name, amount, due_date)

        db.execute("INSERT INTO fees (student_name, class_name, amount, due_date, message, status) VALUES (?, ?, ?, ?, ?, ?)", student_name, class_name, amount, due_date, message, 'Pending')
        return redirect("/fees")
    return render_template("add_fee.html")

@app.route("/delete_fee/<int:id>")
def delete_fee(id):
    if "user_id" not in session:
        return redirect("/login")

    db.execute("DELETE FROM fees WHERE id = ?", id)
    return redirect("/fees")

@app.route("/mark_paid/<int:id>")
def mark_paid(id):
    if "user_id" not in session:
        return redirect("/login")

    print("Marking paid for id:", {id})
    db.execute("UPDATE fees SET status = 'paid' WHERE id = ?", id)
    return redirect("/fees")

@app.route("/fix_status")
def fix_status():
        db.execute("UPDATE fees SET status = 'Pending' WHERE TRIM(LOWER(status)) = 'pending'")
        db.execute("UPDATE fees SET status = 'Paid' WHERE TRIM(LOWER(status)) = 'paid'")
        return redirect("/fees")

@app.route("/updates")
def updates():
    from datetime import date  
    today = date.today().strftime('%Y-%m-%d')
    

    try:
        fees = db.execute("SELECT * FROM fees")
    except:
        fees = []
        
    try:
        homework = db.execute("SELECT * FROM homework WHERE date = ?", today)
    except:
        homework = []
        
    try:
        notices = db.execute("SELECT * FROM notices ORDER BY id DESC")
    except:
        notices = []
        
    try:
        attendance = db.execute("SELECT * FROM attendance WHERE date = ?", today)
    except:
        attendance = []
        
    try:
        teacher_attendance = db.execute("SELECT * FROM teacher_attendance WHERE date = ?", today)
    except:
        teacher_attendance = []

    return render_template("public_updates.html", 
                           fees=fees, 
                           homework=homework, 
                           notices=notices, 
                           attendance=attendance, 
                           teacher_attendance=teacher_attendance,
                           today=today)

@app.route("/clear")
def clear():
    session.clear()
    return "Session Cleared"









    

