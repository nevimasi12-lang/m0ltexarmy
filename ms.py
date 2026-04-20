from flask import Flask, request, session, redirect
from flask_socketio import SocketIO, emit
import sqlite3
import os
import requests

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
                    user_agent TEXT, country TEXT, city TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

def get_real_ip():
    headers = ['CF-Connecting-IP', 'X-Forwarded-For', 'X-Real-IP', 'True-Client-IP']
    for h in headers:
        ip = request.headers.get(h)
        if ip: return ip.split(',')[0].strip()
    return request.remote_addr

def get_location(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon", timeout=3)
        data = r.json()
        if data.get("status") == "success":
            return data.get("country"), data.get("city"), data.get("lat"), data.get("lon")
    except:
        pass
    return "Unknown", "Unknown", None, None

# ====================== HOME ======================
@app.route("/")
def home():
    ip = get_real_ip()
    ua = request.headers.get('User-Agent', 'Unknown')
    ref = request.headers.get('Referer', 'Direct')
    country, city, lat, lon = get_location(ip)

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO visits (ip, user_agent, referrer) VALUES (?, ?, ?)", (ip, ua, ref))
    c.execute("""INSERT INTO unique_visits (ip, first_visit, last_visit, visits, user_agent, country, city)
                 VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, ?, ?, ?)
                 ON CONFLICT(ip) DO UPDATE SET 
                 last_visit=CURRENT_TIMESTAMP, visits=visits+1, country=?, city=?""",
                 (ip, ua, country, city, country, city))
    conn.commit()
    conn.close()

    return """
<html>
<head>
<title>m0ltexArmy</title>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<style>
    body { margin:0; background:#000; color:#00ffcc; font-family:monospace; overflow:hidden; }
    canvas { position:fixed; top:0; left:0; z-index:0; }
    .sidebar { width:70px; height:100vh; background:rgba(10,10,10,0.98); border-right:3px solid #ff0000;
               position:fixed; z-index:10; transition:0.5s; padding:25px 10px; overflow:hidden; }
    .sidebar:hover { width:270px; }
    .sidebar h1 { color:#ff0000; font-size:24px; margin-bottom:40px; white-space:nowrap; }
    .sidebar a { display:block; padding:14px 15px; color:#00ffcc; text-decoration:none; white-space:nowrap; transition:0.3s; }
    .sidebar a:hover { background:#1a0000; color:#ff0000; transform:translateX(15px); }
    .main { margin-left:90px; padding:40px; z-index:1; }
    h1 { color:#ff0000; text-shadow:0 0 20px #ff0000; }
    #terminal { height:520px; background:#000; border:2px solid #ff0000; padding:15px; overflow:auto; box-shadow:0 0 30px #ff0000; }
    #cmd { width:100%; background:#111; border:2px solid #ff0000; color:#00ffcc; padding:14px; margin-top:12px; }
</style>
</head>
<body>
<canvas id="rain"></canvas>
<div class="sidebar">
    <h1>m0ltexArmy</h1>
    <a href="/">Home</a>
    <a href="/shop">Shop</a>
    <a href="/map">Live Map</a>
    <a href="/login">Login</a>
    <a href="/dashboard">Dashboard</a>
</div>
<div class="main">
    <h1>REALTIME TERMINAL v2.5</h1>
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

// Matrix Rain - vylepšený
const canvas = document.getElementById("rain");
const ctx = canvas.getContext("2d");
canvas.height = window.innerHeight;
canvas.width = window.innerWidth;
const chars = "01アイウエオ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
const fontSize = 14;
const drops = Array(Math.floor(canvas.width / fontSize)).fill(1);

function draw() {
    ctx.fillStyle = "rgba(0,0,0,0.07)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#00ff41";
    ctx.font = fontSize + "px monospace";
    for (let i = 0; i < drops.length; i++) {
        const text = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
    }
}
setInterval(draw, 35);
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
            <p><s>99.99$</s> → <strong style="color:#00ff00;">11.99$/rok</strong></p>
            <button onclick="alert('Nákup proběhl úspěšně (simulace)')" style="padding:14px 40px; background:#ff0000; color:black; border:none; cursor:pointer;">Koupit</button>
        </div>
        <div style="background:#111; border:2px solid #ff0000; padding:25px; width:340px;">
            <h2>MM2 Godly + Ancient Set</h2>
            <p><strong>16.99$</strong></p>
            <button onclick="alert('Skins přidány! (simulace)')" style="padding:14px 40px; background:#ff0000; color:black; border:none; cursor:pointer;">Koupit</button>
        </div>
        <div style="background:#111; border:2px solid #ff0000; padding:25px; width:340px;">
            <h2>50 000 Robux</h2>
            <p><strong>24.99$</strong></p>
            <button onclick="alert('Robux přidány na účet (simulace)')" style="padding:14px 40px; background:#ff0000; color:black; border:none; cursor:pointer;">Koupit</button>
        </div>
        <div style="background:#111; border:2px solid #ff0000; padding:25px; width:340px;">
            <h2>Private VPN (3 roky)</h2>
            <p><strong>12.99$</strong></p>
            <button onclick="alert('VPN aktivován (simulace)')" style="padding:14px 40px; background:#ff0000; color:black; border:none; cursor:pointer;">Koupit</button>
        </div>
    </div>
    <br><a href="/" style="color:#ff6666;">← Zpět domů</a>
    </body>
    """

# ====================== LIVE MAP ======================
@app.route("/map")
def map_page():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT ip, country, city, last_visit FROM unique_visits WHERE country != 'Unknown' ORDER BY last_visit DESC LIMIT 50")
    victims = c.fetchall()
    conn.close()

    markers = []
    for ip, country, city, time in victims:
        markers.append(f'["{ip}", "{country}", "{city}", "{time}"]')

    return f"""
    <body style="background:#000; color:#00ffcc; font-family:monospace; margin:0; padding:0;">
    <h1 style="color:#ff0000; text-align:center; padding:15px; background:#111; margin:0;">LIVE VICTIMS MAP</h1>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <div id="map" style="height:calc(100vh - 60px);"></div>
    <script>
        var map = L.map('map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
        
        var victims = [{markers}];
        victims.forEach(v => {{
            L.marker([Math.random()*180-90, Math.random()*360-180]).addTo(map)
             .bindPopup(`<b>${{v[0]}}</b><br>${{v[1]}} - ${{v[2]}}<br>${{v[3]}}`);
        }});
    </script>
    <a href="/" style="position:absolute;top:10px;right:20px;color:#ff6666;z-index:1000;">← Home</a>
    </body>
    """.replace("{markers}", ",".join(markers))

# Login, Dashboard, Logout, Socket...
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
            return "<h2 style='color:red;text-align:center;margin-top:100px;'>Špatné heslo!</h2><a href='/login'>← Zpět</a>"
    return """<body style="background:#000;color:#00ffcc;text-align:center;padding-top:150px;">
    <h1 style="color:#ff0000;">LOGIN</h1>
    <form method="post"><input type="text" name="key" placeholder="Zadej klíč" style="padding:15px;width:300px;"><br><br>
    <button style="padding:12px 40px;background:#ff0000;color:black;border:none;">PŘIHLÁSIT</button></form></body>"""

@app.route("/dashboard")
def dashboard():
    if "role" not in session: return redirect("/login")
    return f"<h1 style='color:#ff0000;text-align:center;margin-top:100px;'>CONTROL PANEL — {session['role'].upper()}</h1><br><a href='/logout'>Logout</a>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

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
    print("✅ m0ltexArmy v2.5 FINAL - Mapa + Shop + Sidebar")
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
