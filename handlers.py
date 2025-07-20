from machine import Pin, Timer
from utils import log_message
import _thread
import time

VALVE_PIN = 2
valve = Pin(VALVE_PIN, Pin.OUT)
timer = Timer(-1)

# Track timer state
timer_active = False
timer_end_time = 0

def route_handler(path):
    global timer_active, timer_end_time

    if path == "/":
        return "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + """
<html>
<head>
    <meta charset="UTF-8">
    <title>Irrigate Control Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            font-size: 2em;
            background: #f2f7f5;
            margin: 0;
            padding: 0;
        }

        .container {
            background: #ffffff;
            padding: 60px 30px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            text-align: center;
            width: 100%;
            max-width: 700px;
            margin: 50px auto;
            box-sizing: border-box;
        }

        h1 {
            margin-top: 0;
            font-size: 2.2em;
            color: #222;
        }

        .button {
            display: inline-block;
            padding: 20px 40px;
            margin: 20px 10px;
            cursor: pointer;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.5em;
            font-weight: 700;
            transition: background-color 0.3s ease, transform 0.2s;
        }

        .button:hover {
            background-color: #45a049;
            transform: scale(1.05);
        }

        .input {
            padding: 16px;
            margin: 20px 0;
            border-radius: 8px;
            border: 2px solid #ccc;
            font-size: 1.5em;
            width: 150px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            font-size: 1.3em;
            color: #444;
        }

        #status {
            margin-top: 30px;
            font-weight: bold;
            font-size: 1.3em;
            color: #333;
        }

        #countdown {
            font-weight: bold;
            font-size: 1.5em;
            color: #007BFF;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Irrigate</h1>
        <button class="button" onclick="controlValve('open')">Open Valve</button>
        <button class="button" onclick="controlValve('close')">Close Valve</button>

        <div style="margin-top: 40px;">
            <label for="duration">Open for duration (minutes):</label>
            <input type="number" id="duration" class="input" min="1" max="30" value="10">
            <button class="button" onclick="openWithDuration()">Start</button>
        </div>

        <p>Time remaining: <span id="countdown">0</span></p>
        <p id="status"></p>
    </div>

    <script>
        function controlValve(action) {
            document.getElementById('status').textContent = 'Processing...';
            fetch('/' + action)
                .then(response => response.text())
                .then(text => {
                    document.getElementById('status').textContent = text;
                })
                .catch(error => {
                    document.getElementById('status').textContent = 'Error: ' + error;
                });
        }

        function openWithDuration() {
            const duration = document.getElementById('duration').value;
            controlValve(`start?duration=${duration}`);
        }

        function updateCountdown() {
            fetch('/status')
                .then(response => response.text())
                .then(seconds => {
                    const s = parseInt(seconds);
                    const m = Math.floor(s / 60);
                    const sec = s % 60;
                    document.getElementById('countdown').textContent = `${m}m ${sec}s`;
                });
        }

        setInterval(updateCountdown, 1000);
    </script>
</body>
</html>
"""



    elif path.startswith("/start?duration="):
        try:
            minutes = int(path.split('=')[1])
            if minutes < 1 or minutes > 60:
                return "HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nDuration must be between 1 and 60 minutes"

            seconds = minutes * 60
            valve.off()
            timer_active = True
            msg = f"Timer set for {minutes} minutes"
            log_message(msg)
            timer_end_time = time.time() + seconds

            def close_valve(t):
                global timer_active
                valve.on()
                timer_active = False
                log_message("Timer expired. Valve closed.")

            timer.init(period=seconds * 1000, mode=Timer.ONE_SHOT, callback=close_valve)

            return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nValve opened for {minutes} minute(s)"

        except ValueError:
            return "HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nInvalid duration format"

    elif path == "/status":
        if timer_active:
            remaining = max(0, int(timer_end_time - time.time()))
            if remaining == 0:
                timer_active = False
        else:
            remaining = 0
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{remaining}"

    elif path == "/open":
        valve.off()  # open valve
        timer.deinit()
        timer_active = False
        timer_end_time = 0
        log_message("Valve Opened Manually")

        def failsafe_close(t):
            msg = "30-minute failsafe triggered. Closing valve."
            print(msg)
            try:
                log_message(msg)
            except Exception as e:
                print("⚠️ Failed to log failsafe event:", e)
    
            valve.on()  # ✅ Always runs


    # Start failsafe timer: 30 min = 1800 seconds
        timer.init(period=30 * 1000, mode=Timer.ONE_SHOT, callback=failsafe_close)

        return "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nValve opened (will auto-close in 30 mins)"

    elif path == "/close":
        valve.on()
        timer.deinit()
        timer_active = False
        timer_end_time = 0
        log_message("Valve Closed manually")
        return "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nValve closed"

    else:
        print(f"No match found - path: '{path}'")
        return "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nInvalid endpoint"



