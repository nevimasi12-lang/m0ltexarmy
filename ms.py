import os
import datetime
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

PORT = int(os.environ.get("PORT", 8080))
WEBHOOK = os.environ.get("WEBHOOK_URL")

visitor_count = 0

def geo_lookup(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        return r
    except:
        return {}

def send_discord(data):
    if not WEBHOOK:
        return
    try:
        requests.post(WEBHOOK, json={
            "content": f"🌍 {data['ip']} | {data['city']}, {data['country']}"
        }, timeout=3)
    except:
        pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global visitor_count
        visitor_count += 1

        ip = self.client_address[0]
        geo = geo_lookup(ip)

        data = {
            "ip": ip,
            "city": geo.get("city", "Unknown"),
            "country": geo.get("country", "Unknown"),
            "lat": geo.get("lat", 50),
            "lon": geo.get("lon", 15),
            "time": str(datetime.datetime.now())
        }

        send_discord(data)

        html = f"""
<!DOCTYPE html>
<html>
<head>
<title>m0ltexArmy</title>

<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>

<style>
body {{
    background: black;
    color: #e6e6e6;
    font-family: Consolas, monospace;
    margin: 0;
    overflow-x: hidden;
}}

.glitch {{
    font-size: 60px;
    text-align: center;
    position: relative;
    animation: glitch 1s infinite;
}}

@keyframes glitch {{
    0% {{ text-shadow: 2px 2px red; }}
    20% {{ text-shadow: -2px -2px cyan; }}
    40% {{ text-shadow: 2px -2px lime; }}
    60% {{ text-shadow: -2px 2px magenta; }}
    80% {{ text-shadow: 2px 2px yellow; }}
    100% {{ text-shadow: none; }}
}}

.container {{
    display: flex;
    justify-content: space-around;
    margin-top: 20px;
}}

.box {{
    border: 1px solid #444;
    padding: 15px;
    width: 300px;
}}

.title {{
    border-bottom: 1px solid #333;
    margin-bottom: 10px;
}}

#map {{
    height: 350px;
    margin: 20px;
    border: 1px solid #333;
}}

#terminal {{
    margin: 20px;
    padding: 10px;
    border: 1px solid #444;
    height: 150px;
    overflow: hidden;
}}
</style>
</head>

<body>

<div class="glitch">m0ltexArmy</div>

<div id="terminal"></div>

<div class="container">

<div class="box">
<div class="title">[ SYSTEM ]</div>
IP: {data["ip"]}<br>
City: {data["city"]}<br>
Country: {data["country"]}<br>
Time: {data["time"]}
</div>

<div class="box">
<div class="title">[ STATUS ]</div>
Visitors: <span id="visits">{visitor_count}</span><br>
Server: ONLINE<br>
Mode: ACTIVE
</div>

<div class="box">
<div class="title">[ MODULES ]</div>
Geo ✔<br>
Map ✔<br>
Webhook ✔<br>
UI ✔
</div>

</div>

<div id="map"></div>

<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<script>
// MAP
var map = L.map('map').setView([{data["lat"]}, {data["lon"]}], 5);

L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);

L.marker([{data["lat"]}, {data["lon"]}]).addTo(map)
    .bindPopup("Visitor").openPopup();

// FAKE TERMINAL
const lines = [
"Initializing m0ltexArmy...",
"Connecting to network...",
"Bypassing firewall...",
"Access granted ✔",
"Loading modules...",
"System ready."
];

let i = 0;
function typeLine() {{
    if (i < lines.length) {{
        document.getElementById("terminal").innerHTML += lines[i] + "<br>";
        i++;
        setTimeout(typeLine, 500);
    }}
}}
typeLine();

// LIVE COUNTER REFRESH
setInterval(() => {{
    fetch(window.location.href)
    .then(() => location.reload());
}}, 15000);

</script>

</body>
</html>
"""

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    print("🔥 m0ltexArmy running...")
    server = ThreadedHTTPServer(("", PORT), Handler)
    server.serve_forever()