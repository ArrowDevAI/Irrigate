import network
from machine import Pin
from handlers import route_handler
from utils import log_message, get_timestamp
import time
import server
from config import SSID, PASSWORD

VALVE_PIN = 2
MAX_LOG_LINES = 50
LOG_FILENAME = "log.txt"

def init_valve():
    print("🔧 Initializing valve...")
    valve = Pin(VALVE_PIN, Pin.OUT)
    valve.on()
    print("✅ Valve initialized to CLOSED state.")
    return valve

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            if not wlan.isconnected():
                print(f"🌐 Connecting to {SSID}... Attempt {attempt + 1}/{max_attempts}")
                wlan.connect(SSID, PASSWORD)
                timeout = 30
                start_time = time.time()
                while not wlan.isconnected():
                    if time.time() - start_time > timeout:
                        print("⏱️ Connection Attempt Timed Out")
                        break
                    time.sleep(1)
            if wlan.isconnected():
                ip_config = wlan.ifconfig()
                print("✅ Connected to Wi-Fi. IP:", ip_config[0])
                return ip_config[0]
        except Exception as e:
            print(f"❌ Wi-Fi error:", e)
            time.sleep(5)
    return None

def main():
    reconnect_interval = 600  # 10 minutes in seconds
    last_check = time.time()

    while True:
        try:
            # Initialize valve to closed on power up
            valve = init_valve()

            # Connect to router
            ip_address = connect_to_wifi()
            
            # If connect_to_wifi() doesn't return anything in the 3 login attempts
            if not ip_address:
                print("❌ Wi-Fi failed. Retrying in 30 seconds...")
                time.sleep(30)
                continue
            # On successful login, start the server
            print("🟢 Launching server in main thread...")
            server.start_server(ip_address, route_handler)

            msg = "⚠️ Socket server exited unexpectedly without exception."
            print(msg)
            log_message(msg)
            time.sleep(5)
            
        # Log an error if login to router is not successful
        
        except Exception as error:
            err = f"💥 Top-level error: {error}"
            print(err)
            log_message(err)
            print("🔁 Restarting in 30 seconds...")
            time.sleep(30)

if __name__ == '__main__':
    main()



