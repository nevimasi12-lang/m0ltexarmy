from flask import Flask, request, redirect, session
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret123"

visits = 0
logs = []

users = {
    "founder": {"password": "1234", "role": "founder"},
    "staff": {"password": "abcd", "role": "staff"}
}

@app.route("/")
def home():
    global visits
    visits += 1

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    logs.append(ip)

    return f"""
    <html>
    <head>
    <style>
    body {{
        margin:0;
        background:black;
        color:white;
        font-family:monospace;
    }}

    h1 {{
        text-align:center;
        font-size:60px;
        margin-top:30px;
        color:white;
        text-shadow: 0 0 10px red, 0 0 25px red;
    }}

    .layout {{
        display:flex;
        padding:20px;
    }}

    .left {{
        width:60%;
        border:1px solid lime;
        box-shadow:0 0 20px lime;
        padding:20px;
        margin-right:10px;
    }}

    .right {{
        width:40%;
        border:1px solid white;
        box-shadow:0 0 20px white;
        padding:20px;
        height:300px;
        overflow:auto;
    }}

    #terminal {{
        height:200px;
    }}

    .bar {{
        height:5px;
        background:lime;
        animation:load 4s forwards;
    }}

    @keyframes load {{
        from {{width:0%;}}
        to {{width:100%;}}
    }}

    button {{
        background:black;
        color:lime;
        border:1px solid lime;
        padding:10px;
        margin:5px;
        cursor:pointer;
    }}

    button:hover {{
        background:lime;
        color:black;
    }}
    </style>

    <script>
    let lines = [
        "Initializing system...",
        "Connecting...",
        "Access granted...",
        "System ready."
    ];

    let i=0;
    function typeLine(){{
        if(i<lines.length){{
            document.getElementById("terminal").innerHTML += lines[i]+"<br>";
            i++;
            setTimeout(typeLine,300);
        }}
    }}

    function fakeCmd(){{
        let el = document.getElementById("cmd");
        let cmds = ["ping server...", "checking users...", "loading data..."];
        setInterval(()=>{{
            el.innerHTML += cmds[Math.floor(Math.random()*cmds.length)]+"<br>";
            el.scrollTop = el.scrollHeight;
        }},1000);
    }}

    function clearTerminal(){{
        document.getElementById("terminal").innerHTML = "";
        i = 0;
        typeLine();
    }}

    window.onload = ()=>{{
        typeLine();
        fakeCmd();
    }};
    </script>
    </head>

    <body>

    <h1>ᴍ𝟘ʟᴛᴇ𝔁𝔸𝕣𝕞𝕪</h1>

    <div class="layout">

        <div class="left">
            <div id="terminal"></div>

            <div class="bar"></div>

            <p style="color:lime;">Visitors: {visits}</p>

            <button onclick="clearTerminal()">Restart Terminal</button>
            <a href="/login"><button>Login Panel</button></a>
        </div>

        <div class="right">
            <div id="cmd"></div>
        </div>

    </div>

    </body>
    </html>
    """

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        pw = request.form["pw"]

        if user in users and users[user]["password"] == pw:
            session["user"] = user
            return redirect("/dashboard")

    return """
    <body style="background:black;color:white;text-align:center;font-family:monospace;">
    <h1>LOGIN</h1>
    <form method="post">
    <input name="user"><br><br>
    <input name="pw" type="password"><br><br>
    <button>Login</button>
    </form>
    </body>
    """

@app.route("/dashboard")
def dash():
    if "user" not in session:
        return redirect("/login")

    role = users[session["user"]]["role"]

    extra = ""

    if role == "founder":
        extra = """
        <form action="/reset">
        <button>RESET VISITS</button>
        </form>

        <form action="/clearlogs">
        <button>CLEAR LOGS</button>
        </form>
        """

    return f"""
    <body style="background:black;color:lime;font-family:monospace;text-align:center;">
    <h1>DASHBOARD ({role})</h1>

    <p>Visitors: {visits}</p>

    {extra}

    <a href="/">Back</a>
    </body>
    """

@app.route("/reset")
def reset():
    global visits
    visits = 0
    return redirect("/dashboard")

@app.route("/clearlogs")
def clearlogs():
    global logs
    logs = []
    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
