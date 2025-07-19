from machine import Pin, Timer
import time
import _thread

VALVE_PIN = 2
valve = Pin(VALVE_PIN, Pin.OUT)
timer = Timer(-1)

def route_handler(path):
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
                        font-size: 2em
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

                
                <p id="status"></p>

                <script>
                    function controlValve(action) {
                        document.getElementById('status').textContent = 'Processing...';
                        fetch('/' + action, {
                            method: 'GET',
                        })
                        .then(response => response.text())
                        .then(text => {
                            document.getElementById('status').textContent = text;
                        })
                        .catch(error => {
                            document.getElementById('status').textContent = 'Error: ' + error;
                        });
                    }
                    
            </body>
        </html>
        """
        else:
                return "HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nInvalid duration"
        except ValueError:
            return "HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nInvalid duration format"
            
    elif path == "/open":
        valve.on()
        return "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nValve opened"
    elif path == "/close":
        valve.off()
        # Cancel any running timer
        timer.deinit()
        return "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nValve closed"
    else:
        print(f"No match found - path: '{path}'")
        return "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nInvalid endpoint"


