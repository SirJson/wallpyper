import socket
from option import Option, Result, Err, Ok
from typing import Any

RPC_ID = 0
RUNNING_CALLS = []
REUSABLE_IDS = []


class JsonRPC():
    def __call__(self, args) ->:
        skeleton = {"jsonrpc": "2.0", "method": "subtract", "params": {}, "id": 3}
        RPC_ID += 1



def test(host="1.1.1.1", port=53, timeout=3) -> Result[None, str]:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return Ok(None)
    except OSError err:
        return Err(f'No internet connection availiable. {err.strerror} ({err.errno})')
