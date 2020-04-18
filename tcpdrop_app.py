# basis of this code is from: https://github.com/cs01/pyxterm.js/blob/master/pyxtermjs/app.py

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
import os
import pty
import subprocess
import select
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.config["fd"] = None
app.config["child_pid"] = None
socketio = SocketIO(app)
to_emit = []

@socketio.on('output')
def parse_output():
  max_read_bytes = 1024 * 20
  while True:
    socketio.sleep(0.01)
    if app.config["fd"]:
      timeout_sec = 0
      (data_ready, _, _) = select.select([app.config["fd"]], [], [], timeout_sec)
      if data_ready:
        output = os.read(app.config["fd"], max_read_bytes).decode()
        output = " ".join(output.split()).strip()
        output = output.split('~')
        if(output[0][0].isdigit()):
          socketio.emit('output', {'output': output[0:9]})
        
@app.route('/')
def index():
  return render_template('index_tcpdrop.html')

@socketio.on('connect')
def connect():
  if app.config['child_pid']:
    return 
  (child_pid, fd) = pty.fork()
  if child_pid == 0:
    subprocess.run(['python', 'tcpdrop.py', '--port', '5000'])
    
  else:
    app.config['fd'] = fd
    app.config['child_pid'] = child_pid
    socketio.start_background_task(target=parse_output)

@socketio.on('disconnect')
def disconnnect():
  print("Bye!")

if __name__ == '__main__':
    socketio.run(app)