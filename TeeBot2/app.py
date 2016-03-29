# -*- coding: utf-8 -*-
__author__ = 'Aleksi Palomäki'
from TeeBot2 import TeeBot
from flask import Flask, request, copy_current_request_context, session, send_from_directory, send_file
from flask_restful import Resource, Api

from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
import os

servers = ["Ene", "Miku", "IA"]


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '****'
socketio = SocketIO(app)


bots = {
    "Ene":  TeeBot.TeeBot("Ene"),
    "Miku": TeeBot.TeeBot("Miku"),
    "IA":   TeeBot.TeeBot("IA"),
}
auth_ids = []

def get_sid():
    return request.__getattr__("sid")

class SendSite(Resource):
    def get(self, path):
        print("Eh?")
        print(os.getcwd()+"\\TeeBot2\\static\\"+path)
        return send_file(os.getcwd()+"\\TeeBot2\\static\\"+path)

class SendCommand(Resource):
    def get(self):
        pass

def emit_info(event):
    print("Emitting {} message.".format(event["emit_type"]))
    socketio.emit(event["emit_type"], event, room=event["room"])


@socketio.on('connect')
def conn_handler():
    socketio.emit("servers", {"servers": servers})
    print("uid is:"+get_sid())

    pass

@socketio.on('event')
def handle_event():
    pass

@socketio.on('server')
def handle_server(server):
    session["room"] = server
    print("Id: {} is now joining room {}".format(request.__getattr__("sid"), server))
    joined_rooms = len(rooms())
    if joined_rooms==1:
        join_room(server)

    bots[server].force_event()


@socketio.on('auth')
def handle_auth(credentials):
    if credentials == "secretpassword" and request.__getattr__("sid") not in auth_ids:
        auth_ids.append(request.__getattr__("sid"))
        print(auth_ids)
        print(rooms())

@socketio.on('message')
def handle_message(message):
    print(request.__dict__)
    print(auth_ids)
    print(rooms())
    if session["room"] is not None and request.__getattr__("sid") in auth_ids:
        bots[session["room"]].writeLine(message)
    else:
        print("user {} was not authenticated".format(request.__getattr__("sid")))


api.add_resource(SendSite, '/site/<path:path>')
api.add_resource(SendCommand, '/send')

for bot in bots:
    botti = bots[bot]
    if botti.listeners[0] is print:
        print(botti.listeners)
        botti.listeners.insert(0, emit_info)
    botti.start()
    print("Starting: {}".format(bot))

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=False, port=5000)