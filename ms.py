from flask import Flask, request, session, redirect
from flask_socketio import SocketIO, emit
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "m0ltex_final_secret"
socketio = SocketIO(app)

# ======================
# 💾 DATABASE
# ======================
def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS visits (ip TEXT, time TEXT)")
    conn.commit()
    conn.close()

init_db()

# 🔐 LOGIN KEYS
USERS = {
    "FOUNDER123": "founder",
    "STAFF123": "staff"
}

online_users = 0

# ======================
# 🌐 HOME
# ======================
@app.route("/")
def home():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO visits VALUES (?, ?)", (ip, datetime.now().strftime("%H:%M:%S")))
    conn.commit()
    conn.close()

    return """
<html>
<head>
<title>m0ltexArmy</title>
<script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>

<style>
body {
    margin:0;
    background:black;
    color:white;
    font-family:monospace;
    display:flex;
}

/* 🌧️ RAIN */
canvas {
    position:fixed;
    top:0;
    left:0;
    z-index:0;
}

/* SIDEBAR */
.sidebar {
    width:220px;
    height:100vh;
    background:#0a0a0a;
    border-right:1px solid red;
    padding:20px;
    z-index:2;
}

.logo {
    font-size:20px;
    margin-bottom:30px;
    text-shadow:0 0 10px red;
}

.menu a {
    display:block;
    margin:12px 0;
    color:white;
    text-decoration:none;
    padding:10px;
    transition:0.3s;
}

.menu a:hover {
    background:red;
    box-shadow:0 0 10px red;
}

/* MAIN */
.main {
    flex:1;
    padding:20px;
    z-index:2;
}

h1 {
    text-shadow:0 0 10px red;
}

/* TERMINAL */
#terminal {
    height:350px;
    background:black;
    border:1px solid red;
    padding:10px;
    overflow:auto;
    box-shadow:0 0 20px red;
}

#cmd {
    width:100%;
    padding:10px;
    background:black;
    border:1px solid red;
    color:white;
    margin-top:10px;
}
</style>
</head>

<body>

<canvas id="rain"></canvas>

<div class="sidebar">
    <div class="logo">ᴍ𝟘ʟᴛᴇ𝔁𝔸𝕣𝕞𝕪</div>

    <div class="menu">
        <a href="/">Home</a>
        <a href="/login">Login</a>
        <a href="#">Shop</a>
        <a href="#">Discord</a>
        <a href="#">YouTube</a>
    </div>
</div>

<div class="main">

<h1>Realtime Terminal</h1>
<p>Online users: <span id="online">0</span></p>

<div id="terminal"></div>
<input id="cmd" placeholder="Type /command...">

</div>

<script>
var socket = io();

let term = document.getElementById("terminal");
let input = document.getElementById("cmd");

socket.on("message", function(msg){
    term.innerHTML += msg + "<br>";
    term.scrollTop = term.scrollHeight;
});

socket.on("online", function(count){
    document.getElementById("online").innerText = count;
});

input.addEventListener("keypress", function(e){
    if(e.key === "Enter"){
        socket.emit("command", input.value);
        input.value = "";
    }
});

/* 🌧️ RAIN */
let c = document.getElementById("rain");
let ctx = c.getContext("2d");

c.height = window.innerHeight;
c.width = window.innerWidth;

let letters = "01";
letters = letters.split("");

let font_size = 14;
let columns = c.width/font_size;

let drops = [];
for(let x=0;x<columns;x++) drops[x]=1;

function draw(){
ctx.fillStyle="rgba(0,0,0,0.05)";
ctx.fillRect(0,0,c.width,c.height);

ctx.fillStyle="red";
ctx.font=font_size+"px monospace";

for(let i=0;i<drops.length;i++){
let text=letters[Math.floor(Math.random()*letters.length)];
ctx.fillText(text,i*font_size,drops[i]*font_size);

if(drops[i]*font_size>c.height && Math.random()>0.975)
drops[i]=0;

drops[i]++;
}
}

setInterval(draw,33);
</script>

</body>
</html>
"""

# ======================
# 🔐 LOGIN
# ======================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        key = request.form.get("key")
        if key in USERS:
            session["role"] = USERS[key]
            return redirect("/dashboard")

    return """
    <body style="background:black;color:white;text-align:center;font-family:monospace;">
    <h1>LOGIN</h1>
    <form method="post">
    <input name="key"><br><br>
    <button>LOGIN</button>
    </form>
    </body>
    """

# ======================
# 📊 DASHBOARD
# ======================
@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/login")

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM visits")
    count = c.fetchone()[0]

    c.execute("SELECT ip, time FROM visits ORDER BY rowid DESC LIMIT 20")
    logs = c.fetchall()
    conn.close()

    logs_html = "<br>".join([f"{ip} | {time}" for ip,time in logs])

    return f"""
    <body style="background:black;color:white;font-family:monospace;">
    <h1 style="text-align:center;">Dashboard</h1>

    <p style="text-align:center;">Total visits: {count}</p>

    <div style="padding:20px;">
    {logs_html}
    </div>

    <a href="/logout">Logout</a>
    </body>
    """

# ======================
# ⚡ SOCKET
# ======================
@socketio.on("connect")
def connect():
    global online_users
    online_users += 1
    emit("online", online_users, broadcast=True)

@socketio.on("disconnect")
def disconnect():
    global online_users
    online_users -= 1
    emit("online", online_users, broadcast=True)

@socketio.on("command")
def command(cmd):
    role = session.get("role","guest")

    if cmd.startswith("/"):
        if cmd == "/help":
            emit("message","Commands: /help /info /clear")

        elif cmd == "/info":
            emit("message",f"Role: {role}")

        elif cmd == "/clear":
            emit("message","Terminal cleared")

        elif cmd == "/admin" and role == "founder":
            emit("message","Founder access granted")

        else:
            emit("message","Unknown command")
    else:
        emit("message",f"You said: {cmd}")

# ======================
# 🔓 LOGOUT
# ======================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ======================
# 🚀 RUN
# ======================
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
