import os
import base64
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from browser_agent import BrowserAgent
import threading
import traceback
from email_generator import generate_email

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Load credentials
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

def emit_status(text, image_path=None):
    socketio.emit("text", text)  # frontend listens to "text"
    if image_path:
        try:
            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode("utf-8")
                img_data_url = f"data:image/png;base64,{encoded}"
                socketio.emit("image", img_data_url)  # frontend listens to "image"
        except Exception as e:
            socketio.emit("text", f"⚠️ Failed to send image for screenshot: {os.path.basename(image_path)}")


def run_browser_task(to, subject, body):
    agent = BrowserAgent(
        GMAIL_USER,
        GMAIL_PASS,
        emit_callback=emit_status
    )
    try:
        emit_status("🧠 Launching browser...")
        if agent.login_to_gmail():
            emit_status("✅ Logged in to Gmail.")
            success = agent.compose_and_send_email(to, subject, body)
            if success:
                emit_status("✅ Email sent successfully!")
            else:
                emit_status("❌ Failed to send email.")
        else:
            emit_status("❌ Gmail login failed.")
    except Exception as e:
        tb = traceback.format_exc()
        emit_status(f"❌ Unexpected error: {str(e)}\n{tb}")
        print(tb)
    finally:
        agent.quit()
        emit_status("🛑 Browser closed.")

@socketio.on("send_email")
def handle_send_email(data):
    to = data.get("to")
    subject = data.get("subject")
    body = data.get("body")
    print(f"Received email request: to={to}, subject={subject}")
    if not (to and subject and body):
        emit("text", "❌ Missing required fields: to, subject, or body.")
        return
    emit("text", f"📨 Preparing to send email to {to}...")
    run_browser_task(to, subject, body)

@socketio.on("generate_email")
def handle_generate(data):
    intent = data.get("intent", "")
    if not intent:
        emit("text", "❌ Please provide a request like 'send a leave email'.")
        return
    emit("text", f"🧠 Generating email for: '{intent}'...")
    result = generate_email(intent)
    emit("generated_email", result)

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route("/socket.io/socket.io.js")
@app.route("/socket.io/socket.io.min.js")  # Add this for fallback
def serve_socketio_js():
    paths_to_check = [
        os.path.join(FRONTEND_DIR, "socket.io.js"),
        os.path.join(FRONTEND_DIR, "socket.io.min.js"),
        os.path.join(FRONTEND_DIR, "..", "node_modules", "socket.io-client", "dist", "socket.io.js")
    ]
    for path in paths_to_check:
        if os.path.exists(path):
            print(f"[INFO] Serving Socket.IO from {path}")
            return send_from_directory(os.path.dirname(path), os.path.basename(path))
    print("[ERROR] socket.io.js not found in any path!")
    return "socket.io.js not found", 404

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
