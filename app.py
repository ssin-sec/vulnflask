from flask import Flask, request, render_template_string, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """)
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'admin123')")
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (2, 'stiv', 'password')")
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        c.execute(query)
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"

    return render_template_string("""
        <h2>Login</h2>
        <form method="POST">
            Username: <input name="username"><br><br>
            Password: <input name="password" type="password"><br><br>
            <input type="submit" value="Login">
        </form>
        <p style="color:red">{{ error }}</p>
    """, error=error)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return f"<h2>Welcome, {session['user']}!</h2><a href='/search'>Search</a> | <a href='/profile?id=1'>Profile</a> | <a href='/logout'>Logout</a>"

@app.route("/search")
def search():
    query = request.args.get("q", "")
    return render_template_string("""
        <h2>Search</h2>
        <form method="GET">
            <input name="q" value="{{ query }}">
            <input type="submit" value="Search">
        </form>
        <p>You searched for: {{ query|safe }}</p>
        <a href='/dashboard'>Back</a>
    """, query=query)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/profile")
def profile():
    user_id = request.args.get("id", "1")
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(f"SELECT id, username FROM users WHERE id = {user_id}")
    user = c.fetchone()
    conn.close()

    if user:
        return render_template_string("""
            <h2>Profile</h2>
            <p>ID: {{ user[0] }}</p>
            <p>Username: {{ user[1] }}</p>
            <a href='/dashboard'>Back</a>
        """, user=user)
    else:
        return "<h2>User not found</h2>", 404

if __name__ == "__main__":
    app.run(debug=True)