import time

def get_timestamp():
    t = time.localtime()
    return "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(*t[:6])

def log_message(msg):
    try:
        line = f"[{get_timestamp()}] {msg}\n"
        print("📝 Writing log:", line.strip())
        with open("log.txt", "a") as f:
            f.write(line)
            f.flush()
    except Exception as e:
        print("❌ Logging error:", e)

