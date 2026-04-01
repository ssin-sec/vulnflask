# VulnFlask: Educational Vulnerable Web Application

VulnFlask is a deliberately insecure Flask application designed for cybersecurity training, penetration testing practice, and learning about common web application vulnerabilities.

**WARNING: DO NOT DEPLOY THIS IN A PRODUCTION ENVIRONMENT.** This application contains several critical security flaws by design. Use only in controlled, isolated environments.

## Features & Intentional Vulnerabilities

This application includes a range of common vulnerabilities (OWASP Top 10) for demonstration purposes:

1.  **SQL Injection (SQLi):**
    *   **Login Bypass:** Authenticate without a valid password (`/login`).
    *   **Data Manipulation:** Inject SQL into profile updates and signup forms (`/settings`, `/signup`).
    *   **Information Disclosure:** Extract database contents through the profile search (`/profile`).

2.  **Command Injection:**
    *   The Network Diagnostic Tool (`/debug`) allows arbitrary shell command execution via the `ip` parameter.

3.  **Cross-Site Scripting (XSS):**
    *   Reflected XSS in the user directory search (`/search`) via the `q` parameter, which is rendered with the `|safe` filter.

4.  **Server-Side Template Injection (SSTI):**
    *   The dashboard (`/dashboard`) uses f-strings inside `render_template_string`, allowing for template injection via the user's session data.

5.  **Path Traversal (LFI):**
    *   The internal file viewer (`/view`) allows reading arbitrary files on the server's filesystem.

6.  **Insecure Direct Object Reference (IDOR):**
    *   User profiles (`/profile`) are accessed via sequential IDs, allowing users to view any profile by modifying the `id` parameter.

## Getting Started

### Prerequisites

-   Python 3.x
-   pip (Python package installer)

### Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Initialize the database (optional):**
    The application will automatically create `users.db` and seed it with initial data if it doesn't exist.

3.  **Run the application:**
    ```bash
    python app.py
    ```
    The app will start on `http://127.0.0.1:5001`.

## Default Credentials
-   **Admin:** `admin` / `admin123`
-   **User:** `bob` / `password`

## Disclaimer
This project is for educational purposes only. Unauthorized use of these techniques against systems you do not have permission to test is illegal. Use responsibly.


Github:https://github.com/ssin-sec
Cybersecurity learning project.
