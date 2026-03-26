🔐 Vulnerable Flask Web App (OWASP Top 10)

This is a deliberately vulnerable web application built with Flask and SQLite to demonstrate common web security vulnerabilities and how they can be exploited and fixed.

⸻

🚀 Setup Instructions
	1.	Clone the repository
	2.	Install dependencies:
pip install -r requirements.txt
	3.	Run the app:
python app.py
	4.	Open in browser:
http://127.0.0.1:5000

⸻

⚠️ Vulnerabilities

1. SQL Injection (Login)

The login system is vulnerable due to unsafe query construction:
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

Exploit:
Username: admin' --
Password: anything
-> logs in without password

2. SQL Injection (Profile)

c.execute(f"SELECT id, username FROM users WHERE id = {user_id}")

Exploit:
/profile?id=1 OR 1=1
-> returns unintended data

3. Cross-Site Scripting (XSS)

<p>You searched for: {{ query|safe }}</p>

Exploit:
<script>alert('XSS')</script>
->executes arbitrary JavaScript in the browser

4. Weak Authentication
	•	Plaintext passwords stored
	•	No hashing or salting

🛡️ Fixes

Fix SQL Injection:
c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))

Fix XSS:
<p>You searched for: {{ query }}</p>

Fix Authentication:
	•	Use password hashing (e.g. bcrypt)
	•	Implement secure session handling

Fix Authentication:
	•	Use password hashing (e.g. bcrypt)
	•	Implement secure session handling

🎯 Purpose

This project demonstrates:
	•	Real-world web vulnerabilities (OWASP Top 10)
	•	Exploitation techniques
	•	Secure coding practices

📌 Future Improvements

	•	CSRF protection
	•	Rate limiting
	•	Logging and monitoring (SIEM integration)

🧠 Author

Github:https://github.com/ssin-sec
Cybersecurity learning project.
