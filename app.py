import os
import re
import sqlite3
import csv
import io
from datetime import datetime
from flask import Flask, render_template_string, request, session, redirect, url_for, Response
from dotenv import load_dotenv

# --- INITIALIZATION ---
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'cyber_sentinel_vault_2026')

ADMIN_USERNAME = os.getenv('ADMIN_USER', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASS', 'password123')

# --- MATURED GLASS-MORPHISM CSS ---
COMMON_CSS = '''
<style>
    :root {
        --bg-dark: #020617;
        --card-bg: #0f172a;
        --text-main: #f8fafc;
        --accent: #38bdf8;
        --danger: #ef4444;
        --success: #22c55e;
        --border: #1e293b;
    }
    body { font-family: 'Inter', sans-serif; background: var(--bg-dark); color: var(--text-main); margin: 0; }
    .navbar { background: #000000; padding: 1rem 2rem; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
    .container { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 85vh; padding: 20px; }
    .glass-card { background: var(--card-bg); padding: 2.5rem; border-radius: 16px; border: 1px solid var(--border); box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); width: 100%; box-sizing: border-box; }
    .status-container { display: flex; align-items: center; gap: 8px; font-size: 0.75rem; color: #64748b; }
    .dot-core { width: 8px; height: 8px; background: var(--success); border-radius: 50%; position: relative; }
    .pulse-dot { width: 100%; height: 100%; border-radius: 50%; background: var(--success); position: absolute; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { transform: scale(1); opacity: 1; } 100% { transform: scale(3); opacity: 0; } }
    input, textarea { width: 100%; padding: 12px; margin: 12px 0; background: #020617; border: 1px solid var(--border); border-radius: 8px; color: white; box-sizing: border-box; }
    .btn { background: var(--accent); color: #020617; border: none; padding: 14px; border-radius: 8px; cursor: pointer; font-weight: 700; width: 100%; transition: 0.2s; text-transform: uppercase; }
    .btn:hover { filter: brightness(1.2); }
    .btn-outline { background: transparent; border: 1px solid var(--border); color: var(--text-main); width: auto; padding: 8px 16px; font-size: 0.8rem; border-radius: 6px; cursor: pointer; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; background: var(--card-bg); }
    th { background: #1e293b; padding: 12px; text-align: left; font-size: 0.7rem; color: var(--accent); text-transform: uppercase; }
    td { padding: 12px; border-top: 1px solid var(--border); font-size: 0.85rem; }
    .badge { padding: 3px 6px; border-radius: 4px; font-size: 0.7rem; background: rgba(239, 68, 68, 0.1); color: var(--danger); border: 1px solid var(--danger); }
    code { color: #facc15; font-family: monospace; }
</style>
'''

# --- DETECTION & DATABASE ---
def get_db():
    conn = sqlite3.connect('security_logs.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS intrusions (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, attack_type TEXT, attacker_ip TEXT, payload TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS blacklist (ip TEXT PRIMARY KEY, reason TEXT, timestamp TEXT)')

def security_scan(payload):
    rules = {
        "SQL Injection": r"('|\-\-|UNION|SELECT|INSERT|DELETE|DROP|OR\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?)",
        "XSS (Scripting)": r"(<script.*?>|alert\(|onerror|onload|javascript:|eval\()",
        "Path Traversal": r"(\.\.\/|\.\.\\|/etc/passwd)"
    }
    for attack, pattern in rules.items():
        if re.search(pattern, payload, re.IGNORECASE): return attack
    return None

# --- MIDDLEWARE: BLACKLIST CHECK ---
@app.before_request
def check_blacklist():
    if request.path.startswith('/admin') or request.path.startswith('/static'): return
    with get_db() as conn:
        if conn.execute('SELECT 1 FROM blacklist WHERE ip = ?', (request.remote_addr,)).fetchone():
            return f"{COMMON_CSS}<div class='container'><div class='glass-card' style='border-color:var(--danger)'><h1>ACCESS DENIED</h1><p>Your IP ({request.remote_addr}) is blacklisted for security violations.</p></div></div>", 403

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.form.get('data', '')
        attack = security_scan(data)
        if attack:
            with get_db() as conn:
                conn.execute('INSERT INTO intrusions (timestamp, attack_type, attacker_ip, payload) VALUES (?, ?, ?, ?)',
                             (datetime.now().strftime("%H:%M:%S"), attack, request.remote_addr, data))
            return f"{COMMON_CSS}<div class='container'><div class='glass-card' style='border-color:var(--danger)'><h2 style='color:var(--danger)'>THREAT DETECTED</h2><p>Pattern matching identified a <b>{attack}</b>.</p><a href='/'><button class='btn'>Back</button></a></div></div>", 403
        return f"{COMMON_CSS}<div class='container'><div class='glass-card'><h2>Success</h2><p>Message sent safely.</p><a href='/'><button class='btn'>Back</button></a></div></div>"

    return f'''{COMMON_CSS}
    <div class="navbar"><strong>🛡 AZ CYBER-SENTINEL</strong></div>
    <div class="container"><div class="glass-card" style="max-width:500px">
        <h2>Secure Portal</h2>
        <form method="POST">
            <textarea name="data" rows="5" placeholder="Test security here..."></textarea>
            <button type="submit" class="btn">Transmit</button>
        </form>
        <br><a href="/login" style="color:#64748b; font-size:0.7rem; text-decoration:none;">Admin Login</a>
    </div></div>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('user') == ADMIN_USERNAME and request.form.get('pass') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
    return f'''{COMMON_CSS}<div class="container"><div class="glass-card" style="max-width:400px">
        <h2>Auth Required</h2>
        <form method="POST">
            <input name="user" placeholder="Admin ID">
            <input name="pass" type="password" placeholder="Passkey">
            <button type="submit" class="btn">Login</button>
        </form>
    </div></div>'''

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    with get_db() as conn:
        logs = conn.execute('SELECT * FROM intrusions ORDER BY id DESC').fetchall()
        stats = conn.execute('SELECT attack_type, COUNT(*) as count FROM intrusions GROUP BY attack_type').fetchall()
        # Fetch current blacklist entries
        blacklist = conn.execute('SELECT * FROM blacklist ORDER BY timestamp DESC').fetchall()
        banned_ips = [row['ip'] for row in blacklist]
    
    chart_labels = [r['attack_type'] for r in stats]
    chart_data = [r['count'] for r in stats]

    # --- LOG TABLE GENERATION ---
    table_rows = ""
    for l in logs:
        is_banned = l['attacker_ip'] in banned_ips
        action_btn = f'<span style="color:var(--danger); font-size:11px;">🔒 BANNED</span>' if is_banned else \
                     f'<a href="/admin/blacklist/{l["attacker_ip"]}"><button class="btn-outline" style="color:var(--danger); border-color:var(--danger); padding:4px 8px; font-size:10px;">🚫 BLOCK</button></a>'
        
        table_rows += f"<tr><td>{l['timestamp']}</td><td><span class='badge'>{l['attack_type']}</span></td><td>{l['attacker_ip']}</td><td><code>{l['payload']}</code></td><td style='text-align:right;'>{action_btn}</td></tr>"

    # --- BLACKLIST TABLE GENERATION ---
    blacklist_rows = ""
    for b in blacklist:
        blacklist_rows += f"""
            <tr>
                <td>{b['ip']}</td>
                <td>{b['timestamp']}</td>
                <td style="text-align:right;">
                    <a href="/admin/unblock/{b['ip']}"><button class="btn-outline" style="color:var(--success); border-color:var(--success); padding:4px 8px; font-size:10px;">🔓 UNBLOCK</button></a>
                </td>
            </tr>"""

    return f'''{COMMON_CSS}
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <div class="navbar">
        <div style="display:flex; align-items:center; gap:15px;"><strong>🛡 CYBER-SENTINEL</strong><div class="status-container"><div style="position:relative; width:8px; height:8px;"><div class="pulse-dot"></div><div class="dot-core"></div></div>ENGINE ACTIVE</div></div>
        <a href="/logout" style="color:var(--danger); text-decoration:none; font-size:0.8rem; font-weight:bold;">DISCONNECT</a>
    </div>

    <div style="padding: 2rem; max-width: 1200px; margin: auto;">
        <div style="display:grid; grid-template-columns: 1fr 2fr; gap:1.5rem; margin-bottom:2rem;">
            <div class="glass-card" style="text-align:center; display:flex; flex-direction:column; justify-content:center;">
                <p style="color:#64748b; font-size:0.7rem; font-weight:bold;">THREATS BLOCKED</p>
                <h1 style="font-size:3rem; color:var(--danger); margin:10px 0;">{len(logs)}</h1>
            </div>
            <div class="glass-card" style="height:200px;"><canvas id="threatChart"></canvas></div>
        </div>

        <h3 style="margin-bottom:1rem;">Live Incident Feed</h3>
        <div class="glass-card" style="padding:0; overflow:hidden; margin-bottom:3rem;">
            <table style="margin:0;">
                <thead><tr><th>Time</th><th>Type</th><th>IP Address</th><th>Payload</th><th style="text-align:right;">Action</th></tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        </div>

        <h3 style="color:var(--danger); margin-bottom:1rem;">Access Control List (Blacklist)</h3>
        <div class="glass-card" style="padding:0; overflow:hidden;">
            <table style="margin:0;">
                <thead><tr><th>Banned IP</th><th>Date Banned</th><th style="text-align:right;">Management</th></tr></thead>
                <tbody>{blacklist_rows if blacklist_rows else "<tr><td colspan='3' style='text-align:center; color:#64748b;'>No active bans</td></tr>"}</tbody>
            </table>
        </div>
    </div>

    <script>
        new Chart(document.getElementById('threatChart'), {{
            type: 'bar',
            data: {{ labels: {chart_labels}, datasets: [{{ data: {chart_data}, backgroundColor: '#38bdf8', borderRadius: 4 }}] }},
            options: {{ responsive:true, maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}, scales:{{y:{{grid:{{color:'#1e293b'}},ticks:{{color:'#64748b'}}}},x:{{ticks:{{color:'#64748b'}}}} }} }}
        }});
    </script>'''

@app.route('/admin/blacklist/<ip>')
def blacklist_ip(ip):
    if not session.get('logged_in'): return redirect(url_for('login'))
    with get_db() as conn:
        conn.execute('INSERT OR IGNORE INTO blacklist VALUES (?, ?, ?)', (ip, "Malicious Input", datetime.now().strftime("%Y-%m-%d")))
    return redirect(url_for('admin_dashboard'))
@app.route('/admin/delete_log/<int:log_id>')

def delete_log(log_id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    query_db('DELETE FROM intrusions WHERE id = ?', [log_id])
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/unblock/<ip>')
def unblock_ip(ip):
    if not session.get('logged_in'): return redirect(url_for('login'))
    with get_db() as conn:
        conn.execute('DELETE FROM blacklist WHERE ip = ?', (ip,))
        conn.commit() # Important: make sure changes are saved
   

@app.route('/admin/export')
def export_logs():
    if not session.get('logged_in'): return redirect(url_for('login'))
    with get_db() as conn: logs = conn.execute('SELECT * FROM intrusions').fetchall()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Time', 'Type', 'IP', 'Payload'])
    for l in logs: cw.writerow([l['timestamp'], l['attack_type'], l['attacker_ip'], l['payload']])
    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=report.csv"})

@app.route('/admin/clear')
def clear_logs():
    if session.get('logged_in'):
        with get_db() as conn: conn.execute('DELETE FROM intrusions')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

    