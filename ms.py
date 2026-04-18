from flask import Flask, request, session, redirect
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "m0ltex_secret_2026"

# ======================
# 💾 DATABASE INIT
# ======================
def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# 🔐 LOGIN KEYS
USERS = {
    "FOUNDER123": "founder",
    "STAFF123": "staff"
}

# ======================
# 🌐 MAIN PAGE
# ======================
@app.route("/")
def home():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO visits (ip, time) VALUES (?, ?)", (ip, datetime.now().strftime("%H:%M:%S")))
    conn.commit()
    conn.close()

    return """
    <html>
    <head>
    <title>m0ltexArmy</title>

    <style>
    body {
        margin:0;
        background:#050505;
        color:white;
        font-family:monospace;
        display:flex;
    }

    /* 🔥 SIDEBAR */
    .sidebar {
        width:220px;
        height:100vh;
        background:#0a0a0a;
        border-right:1px solid red;
        box-shadow:0 0 20px red;
        padding:20px;
    }

    .sidebar h2 {
        color:white;
        text-shadow:0 0 10px red;
    }

    .menu a {
        display:block;
        margin:15px 0;
        color:white;
        text-decoration:none;
        padding:8px;
        border:1px solid transparent;
    }

    .menu a:hover {
        border:1px solid red;
        box-shadow:0 0 10px red;
    }

    /* 🔥 MAIN */
    .main {
        flex:1;
        padding:40px;
        text-align:center;
    }

    h1 {
        font-size:70px;
        text-shadow:0 0 10px red,0 0 40px red;
    }

    .box {
        margin-top:50px;
        padding:30px;
        background:rgba(0,0,0,0.8);
        border-radius:10px;
        box-shadow:0 0 20px red;
    }
    </style>
    </head>

    <body>

    <div class="sidebar">
        <h2>MENU</h2>
        <div class="menu">
            <a href="/login">Login</a>
            <a href="#">Shop</a>
            <a href="#">Discord</a>
            <a href="#">YouTube</a>
            <a href="#">Info</a>
        </div>
    </div>

    <div class="main">
        <h1>ᴍ𝟘ʟᴛᴇ𝔁𝔸𝕣𝕞𝕪</h1>

        <div class="box">
            <p>Welcome to the system</p>
        </div>
    </div>

    </body>
    </html>
    """

# ======================
# 🔐 LOGIN PAGE
# ======================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        key = request.form.get("key")

        if key in USERS:
            session["role"] = USERS[key]
            return redirect("/dashboard")

    return """
    <html>
    <body style="background:#050505;color:white;font-family:monospace;text-align:center;">

    <h1 style="text-shadow:0 0 10px red;">LOGIN</h1>

    <form method="post">
        <input name="key" placeholder="Enter key" style="padding:10px;background:black;border:1px solid red;color:white;">
        <br><br>
        <button style="padding:10px;background:black;border:1px solid red;color:white;">LOGIN</button>
    </form>

    </body>
    </html>
    """

# ======================
# 📊 DASHBOARD
# ======================
@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/login")

    role = session["role"]

    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM visits")
    count = c.fetchone()[0]

    c.execute("SELECT ip, time FROM visits ORDER BY id DESC LIMIT 20")
    logs = c.fetchall()

    conn.close()

    logs_html = "<br>".join([f"{ip} | {time}" for ip, time in logs])

    founder_panel = ""
    if role == "founder":
        founder_panel = """
        <button onclick="location.href='/clear_db'">CLEAR DATABASE</button>
        """

    return f"""
    <html>
    <body style="background:#050505;color:white;font-family:monospace;">

    <h1 style="text-align:center;text-shadow:0 0 10px red;">Dashboard ({role})</h1>

    <div style="display:flex;padding:20px;gap:20px;">

        <div style="flex:1;background:#0a0a0a;padding:20px;border-radius:10px;box-shadow:0 0 15px red;">
            <h3>Stats</h3>
            <p>Total visits: {count}</p>

            <button onclick="location.reload()">Refresh</button>
            <button onclick="location.href='/logout'">Logout</button>

            {founder_panel}
        </div>

        <div style="flex:1;background:#0a0a0a;padding:20px;border-radius:10px;box-shadow:0 0 15px red;">
            <h3>Logs</h3>
            <div style="height:300px;overflow:auto;background:black;padding:10px;border:1px solid red;">
                {logs_html}
            </div>
        </div>

    </div>

    </body>
    </html>
    """

# ======================
# 🔥 FOUNDER ONLY
# ======================
@app.route("/clear_db")
def clear_db():
    if session.get("role") != "founder":
        return "Access denied"

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("DELETE FROM visits")
    conn.commit()
    conn.close()

    return redirect("/dashboard")

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
