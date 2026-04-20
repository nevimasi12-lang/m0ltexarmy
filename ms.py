from flask import Flask, request, session, redirect
from flask_socketio import SocketIO, emit
import sqlite3
import os
import hashlib

app = Flask(__name__)
app.secret_key = "m0ltex_final_secret_2026"
socketio = SocketIO(app, cors_allowed_origins="*")

# ======================
# DATABASE
# ======================
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
    for header in ['CF-Connecting-IP', 'X-Forwarded-For', 'X-Real-IP']:
        ip = request.headers.get(header)
        if ip: return ip.split(',')[0].strip()
    return request.remote_addr

# ======================
# HOME
# ======================
@app.route("/")
def home():
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

    return """
<html>
<head>
<title>m0ltexArmy</title>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<style>
    body { margin:0; background:#0a0a0a; color:#00ffcc; font-family:monospace; overflow:hidden; }
    canvas { position:fixed; top:0; left:0; z-index:0; }
    .sidebar { width:260px; height:100vh; background:#111; border-right:2px solid #ff0000; padding:25px; position:fixed; z-index:2; }
    .main { margin-left:280px; padding:40px; z-index:1; }
    h1 { color:#ff0000; text-shadow:0 0 15px #ff0000; }
    #terminal { height:480px; background:#000; border:2px solid #ff0000; padding:15px; overflow:auto; box-shadow:0 0 30px #ff0000; color:#00ffcc; }
    #cmd { width:100%; background:#111; border:2px solid #ff0000; color:#00ffcc; padding:14px; font-family:monospace; margin-top:12px; }
    .red { color:#ff0000; }
    a { color:#00ffcc; text-decoration:none; }
    a:hover { color:#ff0000; }
</style>
</head>
<body>
<canvas id="rain"></canvas>
<div class="sidebar">
    <h1>m0ltexArmy</h1>
    <p><a href="/">Home</a></p>
    <p><a href="/shop">Shop</a></p>
    <p><a href="/login">Login</a></p>
</div>
<div class="main">
    <h1>REALTIME TERMINAL v2.1</h1>
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

// Matrix Rain
const c = document.getElementById("rain");
const ctx = c.getContext("2d");
c.height = window.innerHeight; c.width = window.innerWidth;
const chars = "01アイウエオネオハッキング".split("");
const fontSize = 15;
const drops = Array(Math.floor(c.width / fontSize)).fill(1);

function draw() {
    ctx.fillStyle = "rgba(10,10,10,0.05)";
    ctx.fillRect(0,0,c.width,c.height);
    ctx.fillStyle = "#00ffcc";
    ctx.font = fontSize + "px monospace";
    for(let i=0; i<drops.length; i++){
        const text = chars[Math.floor(Math.random()*chars.length)];
        ctx.fillText(text, i*fontSize, drops[i]*fontSize);
        if(drops[i]*fontSize > c.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
    }
}
setInterval(draw, 35);
</script>
</body>
</html>
"""

# ======================
# LOGIN (opraveno)
# ======================
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
            return "<h2 style='color:red;text-align:center;margin-top:100px;'>Špatné heslo!</h2><br><a href='/login'>Zpět</a>"
    return """
    <body style="background:#0a0a0a;color:#00ffcc;font-family:monospace;text-align:center;padding-top:120px;">
    <h1 style="color:#ff0000;">m0ltexArmy LOGIN</h1>
    <form method="post">
        <input type="text" name="key" placeholder="Zadej klíč" style="padding:15px;width:320px;background:#111;border:2px solid #ff0000;color:#00ffcc;font-size:16px;"><br><br>
        <button style="padding:12px 40px;background:#ff0000;color:black;border:none;font-size:16px;cursor:pointer;">PŘIHLAŠIT SE</button>
    </form>
    </body>
    """

# ======================
# SHOP (nová funkční stránka)
# ======================
@app.route("/shop")
def shop():
    return """
    <body style="background:#0a0a0a;color:#00ffcc;font-family:monospace;padding:40px;">
    <h1 style="color:#ff0000;">m0ltexArmy SHOP</h1>
    <p><strong>Brzy otevřeme plný shop...</strong></p>
    <div style="background:#111;padding:20px;border:1px solid #ff0000;margin:20px 0;">
        <h2>🔥 VIP Přístup - 15.99$</h2>
        <p>Neomezený přístup + exkluzivní nástroje</p>
        <button onclick="alert('Platba simulována - díky!')">Koupit</button>
    </div>
    <a href="/">← Zpět domů</a>
    </body>
    """

# ======================
# DASHBOARD + SOCKET + LOGOUT
# ======================
@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/login")
    return f"""
    <body style="background:#0a0a0a;color:#00ffcc;font-family:monospace;padding:30px;">
    <h1 style="color:#ff0000;">CONTROL PANEL - {session['role'].upper()}</h1>
    <p>Vítej zpět, máš plný přístup.</p>
    <a href="/logout">Logout</a>
    </body>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# SocketIO
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
    if cmd == "/help":
        emit("message", "Dostupné příkazy: /help, /info, /clear, /stats")
    elif cmd == "/info":
        emit("message", f"Role: {session.get('role', 'guest')}")
    elif cmd == "/clear":
        emit("message", "<span style='color:#ff0000;'>Terminal vyčištěn.</span>")
    else:
        emit("message", f"Neznámý příkaz: {cmd}")

if __name__ == "__main__":
    print("✅ m0ltexArmy v2.1 Spuštěno")
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
