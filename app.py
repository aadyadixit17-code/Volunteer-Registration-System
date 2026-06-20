from flask import Flask, render_template, request, Response, redirect
import sqlite3

app = Flask(__name__)


# ---------------- HOME / REGISTER ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        skills = request.form["skills"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO volunteers(name, email, phone, skills) VALUES(?,?,?,?)",
            (name, email, phone, skills)
        )

        conn.commit()
        conn.close()

        return "<h2>Registration Successful!</h2>"

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    search = request.args.get("search", "")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Total Volunteers
    cursor.execute("SELECT COUNT(*) FROM volunteers")
    total_volunteers = cursor.fetchone()[0]

    if search:
        cursor.execute(
            "SELECT * FROM volunteers WHERE name LIKE ?",
            ('%' + search + '%',)
        )
    else:
        cursor.execute("SELECT * FROM volunteers")

    volunteers = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        volunteers=volunteers,
        total_volunteers=total_volunteers
    )
# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM volunteers")
            volunteers = cursor.fetchall()

            conn.close()

            return render_template("dashboard.html", volunteers=volunteers)

        return "Invalid Username or Password"

    return render_template("login.html")


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM volunteers WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # GET existing data
    cursor.execute("SELECT * FROM volunteers WHERE id=?", (id,))
    volunteer = cursor.fetchone()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        skills = request.form["skills"]

        cursor.execute("""
            UPDATE volunteers
            SET name=?, email=?, phone=?, skills=?
            WHERE id=?
        """, (name, email, phone, skills, id))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    conn.close()

    return render_template("edit.html", volunteer=volunteer)


# ---------------- DOWNLOAD CSV ----------------
@app.route("/download")
def download():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM volunteers")
    volunteers = cursor.fetchall()

    conn.close()

    csv_data = "ID,Name,Email,Phone,Skills\n"

    for v in volunteers:
        csv_data += f"{v[0]},{v[1]},{v[2]},{v[3]},{v[4]}\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=volunteers.csv"
        }
    )
@app.route("/logout")
def logout():
    return redirect("/login")
# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)