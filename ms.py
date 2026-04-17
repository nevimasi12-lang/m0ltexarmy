from flask import Flask, request, session, redirect, url_for
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # změň klidně

visits = 0
logs = []

# 🔐 LOGIN DATA (můžeš změnit)
USERS = {
    "FOUNDER123": "founder",
    "STAFF123": "staff"
}

# ======================
# 🌐 MAIN PAGE
# ======================
@app.route("/")
def home():
    global visits
    visits += 1

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    logs.append(f"[{datetime.now()}] {ip}")

    return f"""
    <html>
    <head>
    <title>m0ltexArmy</title>

    <style>
    body {{
        margin: 0;
        background: #050505;
        color: white;
        font-family: monospace;
    }}

    h1 {{
        text-align: center;
        font-size: 60px;
        color: white;
        text-shadow: 0 0 10px red, 0 0 30px red;
    }}

    .box {{
        width: 80%;
        margin: 40px auto;
        padding: 20px;
        background: rgba(0,0,0,0.8);
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(255,0,0,0.3);
    }}

    input {{
        width: 100%;
        padding: 10px;
        margin-top: 10px;
        background: black;
        border: 1px solid white;
        color: white;
    }}

    button {{
        width: 100%;
        margin-top: 10px;
        padding: 10px;
        background: transparent;
        border: 1px solid red;
        color: white;
        cursor: pointer;
    }}

    button:hover {{
        background: red;
    }}
    </style>
    </head>

    <body>

    <h1>ᴍ𝟘ʟᴛᴇ𝔁𝔸𝕣𝕞𝕪</h1>

    <div class="box">
        <h3>Access Panel</h3>
        <form method="POST" action="/login">
            <input name="key" placeholder="Enter key">
            <button type="submit">Login</button>
        </form>
    </div>

    </body>
    </html>
    """


# ======================
# 🔐 LOGIN SYSTEM
# ======================
@app.route("/login", methods=["POST"])
def login():
    key = request.form.get("key")

    if key in USERS:
        session["role"] = USERS[key]
        return redirect("/dashboard")

    return "Wrong key"


# ======================
# 📊 DASHBOARD
# ======================
@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/")

    role = session["role"]

    log_html = "<br>".join(logs[-20:])

    founder_extra = ""
    if role == "founder":
        founder_extra = """
        <button onclick="window.location='/clear_logs'">Clear Logs</button>
        """

    return f"""
    <html>
    <head>
    <title>Dashboard</title>

    <style>
    body {{
        background: #050505;
        color: white;
        font-family: monospace;
    }}

    h1 {{
        text-align: center;
        color: white;
        text-shadow: 0 0 10px red;
    }}

    .container {{
        display: flex;
        gap: 20px;
        padding: 20px;
    }}

    .panel {{
        flex: 1;
        background: rgba(0,0,0,0.8);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(255,255,255,0.2);
    }}

    .logs {{
        height: 300px;
        overflow-y: auto;
        background: black;
        padding: 10px;
        border: 1px solid white;
    }}

    button {{
        width: 100%;
        margin-top: 10px;
        padding: 10px;
        border: 1px solid red;
        background: transparent;
        color: white;
        cursor: pointer;
    }}

    button:hover {{
        background: red;
    }}
    </style>
    </head>

    <body>

    <h1>Dashboard ({role.upper()})</h1>

    <div class="container">

        <div class="panel">
            <h3>Stats</h3>
            <p>Visitors: {visits}</p>

            <button onclick="window.location.reload()">Refresh</button>
            <button onclick="window.location='/logout'">Logout</button>

            {founder_extra}
        </div>

        <div class="panel">
            <h3>Visitor Logs</h3>
            <div class="logs">{log_html}</div>
        </div>

    </div>

    </body>
    </html>
    """


# ======================
# 🔥 FOUNDER ONLY
# ======================
@app.route("/clear_logs")
def clear_logs():
    if session.get("role") != "founder":
        return "Access denied"

    logs.clear()
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
