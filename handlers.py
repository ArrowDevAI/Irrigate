from machine import Pin, Timer
import time
import _thread

VALVE_PIN = 2
valve = Pin(VALVE_PIN, Pin.OUT)
timer = Timer(-1)

# Track timer state
timer_active = False
timer_end_time = 0

def route_handler(path):
    global timer_active, timer_end_time

    print("\n--- Route Handler Debug ---")
    print("Received path:", repr(path))
    print("Valve status:", valve.value())

    if path == "/":
        return "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + """
        <html>
            <head>
                <style>
                    body {
                        font-size: 2em;
                    }
                    .button {
                        display: inline-block;
                        padding: 10px 20px;
                        margin: 10px;
                        cursor: pointer;
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 2em;
                    }
                    .button:hover {
                        background-color: #45a049;
                    }
                    .input {
                        padding: 8px;
                        margin: 10px;
                        border-radius: 4px;
                        border: 1px solid #ddd;
                    }
                </style>
            </head>
            <body>
                <h1>Welcome to Irrigate</h1>
                <p>Valve Control:</p>
                <button class="button" onclick="controlValve('open')">Open Valve</button>
                <button class="button" onclick="controlValve('close')">Close Valve</button>
                
                <div style="margin-top: 20px;">
                    <label>Open for duration (minutes):</label>
                    <input style="font-size: 2em;" type="number" id="duration" class="input" min="1" max="60" value="5">
                    <button class="button" onclick="openWithDuration()">Start</button>
                </div>

                <p>Time remaining: <span id="countdown">0</span> seconds</p>
                <p id="status"></p>

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
            valve.on()
            timer_active = True
            timer_end_time = time.time() + seconds

            def close_valve(t):
                global timer_active
                valve.off()
                timer_active = False
                print("Timer expired. Valve closed.")

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
        valve.on()
        timer.deinit()
        timer_active = False
        timer_end_time = 0
        return "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nValve opened"

    elif path == "/close":
        valve.off()
        timer.deinit()
        timer_active = False
        timer_end_time = 0
        return "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nValve closed"

    else:
        print(f"No match found - path: '{path}'")
        return "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nInvalid endpoint"
