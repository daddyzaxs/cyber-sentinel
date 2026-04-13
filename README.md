Cyber-Sentinel: Web Intrusion Detection System (WIDS)
📌 Project Overview
Cyber-Sentinel is a lightweight, real-time Web Application Firewall (WAF) and Intrusion Detection System built with Python and Flask. It is designed to sit in front of web forms to detect, block, and log common web attacks such as SQL Injection (SQLi) and Cross-Site Scripting (XSS).

🚀 Features
Real-time Threat Detection: Uses Regex-based pattern matching to identify malicious payloads.

Automated Incident Logging: Every blocked attack is saved to a local SQLite database with the attacker's IP, timestamp, and payload.

Secure Admin Dashboard: A protected interface for security analysts to review logs.

Dark Mode Support: Built-in UI toggle for low-light monitoring environments.

Data Portability: Export incident reports directly to CSV for further forensic analysis.

Environment Security: Utilizes .env files to protect sensitive keys and credentials.

🛠️ Tech Stack
Backend: Python / Flask

Database: SQLite3

Frontend: HTML5, CSS3 (Modern Card UI), JavaScript

Security: Dotenv (Environment Variables), Regex (Pattern Matching)

📂 Project Structure
Plaintext

├── app.py              # Main application logic & security engine
├── .env                # Private keys and admin credentials (Ignored by Git)
├── .gitignore          # Prevents sensitive files from being uploaded
├── security_logs.db    # SQLite database storing intrusion history
└── README.md           # Project documentation
⚙️ Installation & Setup
Clone the repository:

Bash

git clone https://github.com/daddyzaxs/cyber-sentinel.git
cd cyber-sentinel
Install dependencies:

Bash

pip install flask python-dotenv
Configure Environment Variables: Create a .env file in the root directory:

Plaintext

FLASK_SECRET_KEY=your_random_secret_string
ADMIN_USER=admin
ADMIN_PASS=password123
Run the Application:

Bash

python app.py
The site will be live at http://127.0.0.1:5000.

🛡️ Security Logic
The system monitors the POST requests sent to the feedback portal. If a user attempts to input:

' OR 1=1 -- (SQL Injection)

<script>alert('XSS')</script> (Cross-Site Scripting)

The system intercepts the request, returns a 403 Forbidden status, and logs the attacker's details for administrative review.

📸 Dashboard Preview
The Admin Dashboard provides a high-level overview of all blocked attempts.

URL: /admin/dashboard

Functions: Clear Logs, Export to CSV, Theme Toggle.