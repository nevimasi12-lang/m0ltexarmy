from flask import Flask, request
from datetime import datetime
import os

app = Flask(__name__)

visits = 0

@app.route("/")
def home():
    global visits
    visits += 1

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    print(f"[{datetime.now()}] Visitor IP: {ip}")

    return f"""
    <html>
    <head>
        <title>m0ltexArmy</title>

        <style>
            body {{
                background: black;
                color: #e6e6e6;
                font-family: Consolas, monospace;
                margin: 0;
                overflow: hidden;
            }}

            h1 {{
                text-align: center;
                font-size: 70px;
                margin-top: 30px;
                animation: glitch 0.7s infinite;
            }}

            @keyframes glitch {{
                0% {{text-shadow: 3px 3px red;}}
                25% {{text-shadow: -3px 2px cyan;}}
                50% {{text-shadow: 2px -3px purple;}}
                75% {{text-shadow: -2px -2px red;}}
                100% {{text-shadow: 3px 3px cyan;}}
            }}

            #loadingScreen {{
                position: fixed;
                width: 100%;
                height: 100%;
                background: black;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                color: lime;
                font-size: 25px;
                z-index: 999;
            }}

            .bar {{
                width: 0%;
                height: 4px;
                background: lime;
                margin-top: 10px;
                animation: load 3s linear forwards;
            }}

            @keyframes load {{
                0% {{width: 0%;}}
                100% {{width: 100%;}}
            }}

            .container {{
                display: flex;
                justify-content: space-around;
                margin-top: 20px;
            }}

            .box {{
                border: 1px solid #444;
                padding: 15px;
                width: 280px;
                background: rgba(255,255,255,0.03);
            }}

            .title {{
                border-bottom: 1px solid #333;
                margin-bottom: 10px;
            }}

            #terminal {{
                margin: 20px;
                border: 1px solid #333;
                padding: 15px;
                height: 180px;
                overflow-y: auto;
            }}

            #counter {{
                text-align: center;
                margin-top: 10px;
                color: lime;
            }}
        </style>

        <script>
            let lines = [
                "Initializing m0ltexArmy...",
                "Connecting to network...",
                "Bypassing firewall...",
                "Access granted...",
                "Loading modules...",
                "Tracking session...",
                "System ready.",
                "",
                "No nic...",
                "m0ltexArmy na topu 😈"
            ];

            let i = 0;

            function typeLine() {{
                if (i < lines.length) {{
                    let term = document.getElementById("terminal");
                    term.innerHTML += lines[i] + "<br>";
                    term.scrollTop = term.scrollHeight;
                    i++;
                    setTimeout(typeLine, 350);
                }}
            }}

            function startApp() {{
                document.getElementById("loadingScreen").style.display = "none";
                typeLine();
            }}

            window.onload = () => {{
                setTimeout(startApp, 2000);
            }};

            setInterval(() => {{
                location.reload();
            }}, 15000);
        </script>
    </head>

    <body>

        <div id="loadingScreen">
            Loading m0ltexArmy...
            <div class="bar"></div>
        </div>

        <h1>m0ltexArmy</h1>

        <div class="container">

            <div class="box">
                <div class="title">[ SYSTEM ]</div>
                IP: {ip}<br>
                Time: {datetime.now().strftime("%H:%M:%S")}
            </div>

            <div class="box">
                <div class="title">[ STATUS ]</div>
                Server: ONLINE<br>
                Mode: ACTIVE<br>
                Visitors: {visits}
            </div>

            <div class="box">
                <div class="title">[ MODULES ]</div>
                Geo ✔<br>
                UI ✔<br>
                Logs ✔<br>
                Core ✔
            </div>

        </div>

        <div id="terminal"></div>

        <div id="counter">
            Visitors: {visits}
        </div>

    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
