from channels.routing import route
from glos.consumers import importer, ws_message

channel_routing = [
    route('importer', importer),
    route("websocket.receive", ws_message),
]
