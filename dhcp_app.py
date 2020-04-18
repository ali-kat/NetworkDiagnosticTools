# basis of this code is from: https://github.com/cs01/pyxterm.js/blob/master/pyxtermjs/app.py

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
import os
import pty
import subprocess
import select
import json

from dhcp_client import * 

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
client = DHCPClient()
socketio = SocketIO(app)
        
@app.route('/')
def index():
  return render_template('index_dhcp.html')

@socketio.on('discover')
def discover():
	client.discover()
	if client.dhcp_offer == -1:
		socketio.emit('discover', {'discover': -1, 'offer': -1})
		return;
	socketio.emit('discover', {'discover': client.dhcp_discover.show2(dump=True), 'offer': client.dhcp_offer.show2(dump=True)})

@socketio.on('request')
def request():
	client.request()
	if client.dhcp_ack == -1:
		socketio.emit('request', {'request': -1, 'ack': -1})
		return; 
	socketio.emit('request', {'request': client.dhcp_request.show2(dump=True), 'ack': client.dhcp_ack.show2(dump=True)})

@socketio.on('release')
def release():
	client.release() 
	socketio.emit('release', {'release': client.dhcp_release.show2(dump=True)})

@socketio.on('run')
def run():
	if client.dhcp_offer == -1 or client.dhcp_ack == -1:
		socketio.emit('discover', {'discover': -1, 'offer': -1, 'request': -1, 'ack': -1})
		return;
	client.run()
	socketio.emit('run', {'discover': client.dhcp_discover.show2(dump=True), 'offer': client.dhcp_offer.show2(dump=True), 'request': client.dhcp_request.show2(dump=True), 'ack': client.dhcp_ack.show2(dump=True), 'release': client.dhcp_release.show2(dump=True)}) 

@socketio.on('connect')
def connect():
	print("Hello!")

@socketio.on('disconnect')
def disconnnect():
  print("Bye!")

if __name__ == '__main__':
    socketio.run(app)