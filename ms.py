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
                margin: 0;
                background: black;
                color: white;
                font-family: monospace;
                overflow: hidden;
            }}

            /* 🔥 BLUR + GLOW BACKGROUND LOGO */
            .bg-logo {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 600px;
                opacity: 0.08;
                filter: blur(2px);
                animation: pulse 3s infinite;
                z-index: 0;
            }}

            @keyframes pulse {{
                0% {{ opacity: 0.05; transform: translate(-50%, -50%) scale(1); }}
                50% {{ opacity: 0.15; transform: translate(-50%, -50%) scale(1.1); }}
                100% {{ opacity: 0.05; transform: translate(-50%, -50%) scale(1); }}
            }}

            h1 {{
                text-align: center;
                font-size: 60px;
                margin-top: 40px;
                z-index: 2;
                position: relative;
                animation: glitch 1s infinite;
            }}

            @keyframes glitch {{
                0% {{ text-shadow: 2px 2px red; }}
                50% {{ text-shadow: -2px -2px purple; }}
                100% {{ text-shadow: 2px 2px red; }}
            }}

            #terminal {{
                margin: 40px auto;
                width: 80%;
                border: 1px solid lime;
                padding: 20px;
                min-height: 200px;
                z-index: 2;
                position: relative;
                background: rgba(0,0,0,0.7);
                box-shadow: 0 0 20px lime;
            }}

            #counter {{
                text-align: center;
                margin-top: 20px;
                color: lime;
                z-index: 2;
                position: relative;
            }}

            .bar {{
                width: 0%;
                height: 5px;
                background: lime;
                margin-top: 20px;
                animation: load 5s linear forwards;
            }}

            @keyframes load {{
                0% {{ width: 0%; }}
                100% {{ width: 100%; }}
            }}
        </style>

        <script>
            let lines = [
                "Initializing m0ltexArmy...",
                "Connecting to network...",
                "Bypassing firewall...",
                "Access granted...",
                "Injecting payload...",
                "Tracking session...",
                "System ready.",
                "",
                "No nic...",
                "M0ltexArmy na topu 😈"
            ];

            let i = 0;

            function typeLine() {{
                if (i < lines.length) {{
                    let term = document.getElementById("terminal");
                    term.innerHTML += lines[i] + "<br>";
                    i++;
                    setTimeout(typeLine, 300);
                }}
            }}

            window.onload = () => {{
                typeLine();
            }};
        </script>
    </head>

    <body>

        <!-- 🔥 TVOJE LOGO NA POZADÍ -->
        <img src="https://i.imgur.com/hWAaQFK.png" class="bg-logo">

        <h1>m0ltexArmy</h1>

        <div id="terminal"></div>

        <div class="bar"></div>

        <div id="counter">
            Visitors: {visits}
        </div>

    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
