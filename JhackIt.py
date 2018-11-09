import os
import time
import json
import queue
import bottle
import threading

from easy_crack import EasyCrack
from configurator import JhackItConfig

os.chdir("/home/pi/Jhack-It")

config = JhackItConfig()


class HandleCommands(object):

    def __init__(self):
        self._active = False
        self._read_thread = None
        self._command_queue = queue.Queue()

    def _command_thread(self):
        while self._active:
            while not self._command_queue.empty():
                try:
                    pending_command = self._command_queue.get()
                    command_type = pending_command["type"].lower()
                    easycrack_instance = EasyCrack(config.scan_interface)
                    if command_type == "toggle_monitor":
                        easycrack_instance.toggle_monitor()
                    elif command_type == "acquire_target":
                        if "bssid" in pending_command:
                            client = None
                            if "client" in pending_command:
                                client = pending_command["client"]
                            easycrack_instance.acquire_target(pending_command["bssid"], client)
                    elif command_type == "launch_deauths":
                        client = None
                        deauth_count = 10
                        if "client" in pending_command:
                            client = pending_command["client"]
                        if "deauth_count" in pending_command:
                            deauth_count = pending_command["deauth_count"]
                        easycrack_instance.launch_deauths(client, deauth_count)
                    elif command_type == "clear_target":
                        easycrack_instance.clear_target()
                except Exception as e:
                    print("Exception handling command: {0}".format(e))
                continue
            time.sleep(1.0 / 2.0)

    def queue_command(self, command_dict):
        self._command_queue.put(command_dict)

    def start(self):
        self._active = True
        self._read_thread = threading.Thread(target=self._command_thread)
        self._read_thread.setDaemon(True)
        self._read_thread.start()

    def stop(self):
        self._active = False
        self._read_thread.join()


command_handler = HandleCommands()


@bottle.get("/css/<filepath:re:.*\.css>")
def css_get(filepath):
    return bottle.static_file(filepath, root="css")


@bottle.get("/scripts/<filepath:re:.*\.js>")
def js_get(filepath):
    return bottle.static_file(filepath, root="js")
    
@bottle.get("/fonts/<filepath:re:.*\.(eot|otf|svg|ttf|woff|woff2?)>")
def font_get(filepath):
    return bottle.static_file(filepath, root="fonts")

@bottle.get("/api/get_state")
def get_scan_state():
    scan_state = EasyCrack(config.scan_interface).get_scan_state()
    print(scan_state)
    return json.dumps(scan_state)


@bottle.post("/api/command")
def post_scan_command():
    try:
        request = bottle.request.json
        if "type" in request:
            command_handler.queue_command(request)
            return bottle.HTTPResponse(status=201, body='{"error": "success"}')
    except ValueError as e:
        print(e)
    return bottle.HTTPResponse(status=400, body='{"error": "malformed request"}')


@bottle.route("/")
def index():
    return bottle.static_file("index.html", root="html")


if __name__ == "__main__":
    with open("config.json", "r") as infile:
        config = JhackItConfig.from_json(infile.read())
    command_handler.start()
    EasyCrack(config.scan_interface).toggle_monitor()
    bottle.run(host=config.bind_address, port=config.bind_port)
