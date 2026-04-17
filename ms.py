from flask import Flask, request, session, redirect
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "m0ltex_secret_2026"

visits = 0
logs = []

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
    global visits
    visits += 1

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {ip}")

    return f"""
    <html>
    <head>
    <title>m0ltexArmy</title>

    <style>
    body {{
        margin:0;
        background:black;
        font-family:monospace;
        color:white;
        overflow:hidden;
    }}

    h1 {{
        text-align:center;
        margin-top:40px;
        font-size:70px;
        text-shadow:0 0 10px red,0 0 30px red;
    }}

    .panel {{
        width:300px;
        margin:80px auto;
        padding:20px;
        background:rgba(0,0,0,0.9);
        border-radius:10px;
        box-shadow:0 0 20px red;
    }}

    input {{
        width:100%;
        padding:10px;
        background:black;
        border:1px solid red;
        color:white;
        margin-top:10px;
    }}

    button {{
        width:100%;
        margin-top:10px;
        padding:10px;
        border:1px solid red;
        background:black;
        color:white;
        cursor:pointer;
    }}

    button:hover {{
        background:red;
    }}
    </style>
    </head>

    <body>

    <h1>ᴍ𝟘ʟᴛᴇ𝔁𝔸𝕣𝕞𝕪</h1>

    <div class="panel">
        <form method="POST" action="/login">
            <input name="key" placeholder="Enter access key">
            <button>LOGIN</button>
        </form>
    </div>

    </body>
    </html>
    """

# ======================
# 🔐 LOGIN
# ======================
@app.route("/login", methods=["POST"])
def login():
    key = request.form.get("key")

    if key in USERS:
        session["role"] = USERS[key]
        return redirect("/dashboard")

    return "<h1 style='color:red;text-align:center;'>❌ Wrong key</h1>"

# ======================
# 📊 DASHBOARD
# ======================
@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/")

    role = session["role"]
    log_html = "<br>".join(logs[-20:])

    founder_panel = ""
    if role == "founder":
        founder_panel = """
        <button onclick="location.href='/clear_logs'">CLEAR LOGS</button>
        <button onclick="location.href='/reset'">RESET VISITS</button>
        """

    return f"""
    <html>
    <head>
    <style>
    body {{
        background:black;
        color:white;
        font-family:monospace;
    }}

    h1 {{
        text-align:center;
        text-shadow:0 0 15px red;
    }}

    .container {{
        display:flex;
        gap:20px;
        padding:20px;
    }}

    .panel {{
        flex:1;
        background:rgba(0,0,0,0.9);
        padding:20px;
        border-radius:10px;
        box-shadow:0 0 20px red;
    }}

    .logs {{
        height:300px;
        overflow:auto;
        background:black;
        padding:10px;
        border:1px solid red;
    }}

    button {{
        width:100%;
        margin-top:10px;
        padding:10px;
        border:1px solid red;
        background:black;
        color:white;
        cursor:pointer;
    }}

    button:hover {{
        background:red;
    }}
    </style>
    </head>

    <body>

    <h1>DASHBOARD ({role.upper()})</h1>

    <div class="container">

        <div class="panel">
            <h3>Stats</h3>
            <p>Visitors: {visits}</p>

            <button onclick="location.reload()">REFRESH</button>
            <button onclick="location.href='/logout'">LOGOUT</button>

            {founder_panel}
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

@app.route("/reset")
def reset():
    if session.get("role") != "founder":
        return "Access denied"

    global visits
    visits = 0
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
