
"""
Utility functions
"""

import socket
from option import Option, Result, Err, Ok


class Net(object):
    @staticmethod
    def TestConnection(host="1.1.1.1", port=53, timeout=3) -> Result[None, str]:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return Ok(None)
        except OSError err:
            return Err(f'No internet connection availiable. {err.strerror} ({err.errno})')
