from flask import Flask, request, render_template_string, redirect, url_for, session
import sqlite3
import os
import subprocess

app = Flask(__name__)
app.secret_key = "supersecretkey"

CSS = """
<style>
    :root {
        --primary-color: #00ff41;
        --bg-color: #0d0d0d;
        --card-bg: #1a1a1a;
        --text-color: #e0e0e0;
        --border-color: #333;
    }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: var(--bg-color);
        color: var(--text-color);
        margin: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        min-height: 100vh;
    }
    nav {
        width: 100%;
        background: var(--card-bg);
        padding: 1rem 0;
        border-bottom: 2px solid var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
    }
    nav a {
        color: var(--primary-color);
        text-decoration: none;
        margin: 0 15px;
        font-weight: bold;
        transition: 0.3s;
    }
    nav a:hover {
        text-shadow: 0 0 10px var(--primary-color);
    }
    .container {
        width: 90%;
        max-width: 800px;
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    h2 { color: var(--primary-color); border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; }
    input:not([type="submit"]), textarea {
        box-sizing: border-box;
        width: 100%;
        padding: 10px;
        margin: 10px 0;
        background: #000;
        border: 1px solid var(--border-color);
        color: var(--primary-color);
        border-radius: 4px;
        font-size: 1rem;
    }
    input[type="submit"] {
        background: var(--primary-color);
        color: #000;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        cursor: pointer;
        border-radius: 4px;
        transition: 0.3s;
    }
    input[type="submit"]:hover {
        background: #00cc33;
        box-shadow: 0 0 15px var(--primary-color);
    }
    pre {
        background: #000;
        padding: 1rem;
        border-left: 3px solid var(--primary-color);
        overflow-x: auto;
        color: #00ff00;
    }
    .error { color: #ff4444; font-weight: bold; }
    a.back { display: inline-block; margin-top: 1rem; color: #888; text-decoration: none; }
    a.back:hover { color: var(--text-color); }
</style>
"""

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            bio TEXT
        )
    """)
    c.execute("INSERT OR IGNORE INTO users (id, username, password, bio) VALUES (1, 'admin', 'admin123', 'The boss')")
    c.execute("INSERT OR IGNORE INTO users (id, username, password, bio) VALUES (2, 'bob', 'password', 'Hacker in training')")
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
        # VULNERABILITY: SQL Injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        c.execute(query)
        user = c.fetchone()
        conn.close()
        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"

    return render_template_string(CSS + """
        <div class="container">
            <h2>Secure(?) Login</h2>
            <form method="POST">
                <label>Username</label><input type="text" name="username">
                <label>Password</label><input type="password" name="password">
                <input type="submit" value="Authenticate">
            </form>
            <p class="error">{{ error }}</p>
            <p style="margin-top: 1rem; font-size: 0.9rem;">No account? <a href="/signup" style="color: var(--primary-color);">Sign up here</a></p>
        </div>
    """, error=error)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    
    # VULNERABILITY: Server-Side Template Injection (SSTI)
    # The 'f-string' embeds the session username directly into the template string before it's rendered.
    template = CSS + f"""
        <nav>
            <a href='/dashboard'>Dashboard</a>
            <a href='/search'>Search</a>
            <a href='/profile?id=1'>My Profile</a>
            <a href='/settings'>Settings</a>
            <a href='/debug'>Network Debug</a>
            <a href='/logout'>Logout</a>
        </nav>
        <div class="container">
            <h2>System Dashboard</h2>
            <p>Access Granted. Welcome back, <strong>{session['user']}</strong>!</p>
            <hr>
            <h3>Internal Resources</h3>
            <ul>
                <li><a href='/view?file=README.md' style="color:var(--primary-color)">System README</a></li>
                <li><a href='/view?file=app.py' style="color:var(--primary-color)">Source Code (Audit)</a></li>
            </ul>
        </div>
    """
    return render_template_string(template)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    # VULNERABILITY: Cross-Site Scripting (XSS) via |safe
    return render_template_string(CSS + """
        <nav><a href='/dashboard'>Back to Dashboard</a></nav>
        <div class="container">
            <h2>User Directory Search</h2>
            <form method="GET">
                <input name="q" value="{{ query }}" placeholder="Search usernames...">
                <input type="submit" value="Search">
            </form>
            <p>Query results for: <strong>{{ query|safe }}</strong></p>
            <div style="border: 1px solid #333; padding: 10px; color: #888;">
                [No users found matching your query]
            </div>
        </div>
    """, query=query)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        new_bio = request.form.get("bio", "")
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        # VULNERABILITY: SQL Injection in UPDATE
        c.execute(f"UPDATE users SET bio = '{new_bio}' WHERE username = '{session['user']}'")
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    return render_template_string(CSS + """
        <nav><a href='/dashboard'>Back to Dashboard</a></nav>
        <div class="container">
            <h2>Account Settings</h2>
            <form method="POST">
                <label>Update Bio</label>
                <textarea name="bio" rows="4"></textarea>
                <input type="submit" value="Save Changes">
            </form>
        </div>
    """)

@app.route("/profile")
def profile():
    user_id = request.args.get("id", "1")
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    # VULNERABILITY: SQL Injection + IDOR
    try:
        c.execute(f"SELECT id, username, bio FROM users WHERE id = {user_id}")
        user = c.fetchone()
    except:
        user = None
    conn.close()

    if user:
        return render_template_string(CSS + """
            <nav><a href='/dashboard'>Back to Dashboard</a></nav>
            <div class="container">
                <h2>User Profile</h2>
                <p><strong>Internal ID:</strong> {{ user[0] }}</p>
                <p><strong>Username:</strong> {{ user[1] }}</p>
                <p><strong>Biography:</strong> {{ user[2] }}</p>
            </div>
        """, user=user)
    else:
        return "<h2>User not found</h2>", 404

@app.route("/debug")
def debug():
    if "user" not in session:
        return redirect(url_for("login"))
    
    ip = request.args.get("ip", "127.0.0.1")
    # VULNERABILITY: Command Injection
    cmd = f"ping -c 1 {ip}"
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
    except Exception as e:
        output = str(e)

    return render_template_string(CSS + """
        <nav><a href='/dashboard'>Back to Dashboard</a></nav>
        <div class="container">
            <h2>Network Diagnostic Tool</h2>
            <form method="GET">
                <label>Target IP/Hostname</label>
                <input name="ip" value="{{ ip }}">
                <input type="submit" value="Execute Ping">
            </form>
            <p>Command Output:</p>
            <pre>{{ output }}</pre>
        </div>
    """, ip=ip, output=output)

@app.route("/view")
def view_file():
    # VULNERABILITY: Path Traversal
    filename = request.args.get("file", "")
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except Exception as e:
        content = f"Error reading file: {str(e)}"
    
    return render_template_string(CSS + """
        <nav><a href='/dashboard'>Back to Dashboard</a></nav>
        <div class="container">
            <h2>Internal File Viewer</h2>
            <p><strong>File:</strong> {{ filename }}</p>
            <pre>{{ content }}</pre>
        </div>
    """, filename=filename, content=content)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        bio = request.form.get("bio", "New member")

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        try:
            # VULNERABILITY: SQL Injection in INSERT
            # This allows for various exploits, including bypassing unique constraints or even RCE in some DBs
            query = f"INSERT INTO users (username, password, bio) VALUES ('{username}', '{password}', '{bio}')"
            c.execute(query)
            conn.commit()
            return redirect(url_for("login"))
        except Exception as e:
            error = f"Registration failed: {str(e)}"
        finally:
            conn.close()

    return render_template_string(CSS + """
        <div class="container">
            <h2>Create Cyber Account</h2>
            <form method="POST">
                <label>Username</label><input type="text" name="username" required>
                <label>Password</label><input type="password" name="password" required>
                <label>Bio</label><textarea name="bio"></textarea>
                <input type="submit" value="Register Account">
            </form>
            <p class="error">{{ error }}</p>
            <p style="margin-top: 1rem; font-size: 0.9rem;">Already have an account? <a href="/login" style="color: var(--primary-color);">Login here</a></p>
        </div>
    """, error=error)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
