from textual_serve.server import Server

from functions.config import load_config
host, port = load_config().site
print(host)
print(port)

server = Server("python tui.py", host=host, port=port)
server.serve()
