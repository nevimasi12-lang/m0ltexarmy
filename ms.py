from flask import Flask, request
from datetime import datetime

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
                color: white;
                font-family: monospace;
                text-align: center;
            }}

            h1 {{
                font-size: 60px;
                margin-top: 50px;
                animation: glitch 1s infinite;
            }}

            @keyframes glitch {{
                0% {{text-shadow: 2px 2px red;}}
                50% {{text-shadow: -2px -2px purple;}}
                100% {{text-shadow: 2px 2px red;}}
            }}

            #terminal {{
                margin: 40px auto;
                width: 80%;
                border: 1px solid white;
                padding: 20px;
                text-align: left;
                min-height: 200px;
            }}

            #counter {{
                margin-top: 20px;
                color: lime;
            }}

            .bar {{
                width: 0%;
                height: 5px;
                background: lime;
                margin-top: 10px;
                animation: load 4s linear forwards;
            }}

            @keyframes load {{
                0% {{width: 0%;}}
                100% {{width: 100%;}}
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
                "M0ltexArmy na topu 😈"
            ];

            let i = 0;

            function typeLine() {{
                if (i < lines.length) {{
                    let term = document.getElementById("terminal");
                    term.innerHTML += lines[i] + "<br>";
                    i++;
                    setTimeout(typeLine, 400);
                }}
            }}

            window.onload = () => {{
                typeLine();
            }};
        </script>
    </head>

    <body>
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
    app.run(host="0.0.0.0", port=8080)
