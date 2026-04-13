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

            /* 🔥 ULTRA VIDITELNÉ LOGO */
            .bg-logo {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 700px;
                opacity: 0.3;
                animation: pulse 2s infinite, glitchLogo 0.4s infinite;
                z-index: 0;
            }}

            @keyframes pulse {{
                0% {{ opacity: 0.2; transform: translate(-50%, -50%) scale(1); }}
                50% {{ opacity: 0.5; transform: translate(-50%, -50%) scale(1.15); }}
                100% {{ opacity: 0.2; transform: translate(-50%, -50%) scale(1); }}
            }}

            @keyframes glitchLogo {{
                0% {{ filter: blur(1px) brightness(1); }}
                20% {{ filter: blur(4px) brightness(2); }}
                40% {{ filter: blur(0px) brightness(0.5); }}
                60% {{ filter: blur(3px) brightness(1.5); }}
                80% {{ filter: blur(1px) brightness(0.7); }}
                100% {{ filter: blur(1px) brightness(1); }}
            }}

            h1 {{
                text-align: center;
                font-size: 65px;
                margin-top: 40px;
                z-index: 2;
                position: relative;
                animation: glitchText 0.6s infinite;
            }}

            @keyframes glitchText {{
                0% {{ text-shadow: 3px 3px red; }}
                25% {{ text-shadow: -3px 2px cyan; }}
                50% {{ text-shadow: 2px -3px purple; }}
                75% {{ text-shadow: -2px -2px red; }}
                100% {{ text-shadow: 3px 3px cyan; }}
            }}

            #terminal {{
                margin: 40px auto;
                width: 80%;
                border: 1px solid lime;
                padding: 20px;
                min-height: 200px;
                z-index: 2;
                position: relative;
                background: rgba(0,0,0,0.8);
                box-shadow: 0 0 25px lime;
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
                animation: load 4s linear forwards;
            }}

            @keyframes load {{
                0% {{ width: 0%; }}
                100% {{ width: 100%; }}
            }}

            /* 💀 FLASH EFEKT */
            body::after {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: white;
                opacity: 0;
                animation: flash 6s infinite;
                pointer-events: none;
            }}

            @keyframes flash {{
                0% {{ opacity: 0; }}
                95% {{ opacity: 0; }}
                96% {{ opacity: 0.4; }}
                100% {{ opacity: 0; }}
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
                    term.scrollTop = term.scrollHeight;
                    i++;
                    setTimeout(typeLine, 250);
                }}
            }}

            window.onload = () => {{
                typeLine();
            }};
        </script>
    </head>

    <body>

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
