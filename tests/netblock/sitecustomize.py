"""Block all network access for any Python process that starts with this dir on PYTHONPATH.

Used by tests and CI to prove replay mode is fully offline: any socket
connect / DNS lookup raises, including in pytest child processes.
"""

import socket


class NetworkBlocked(RuntimeError):
    pass


def _blocked(*_args, **_kwargs):
    raise NetworkBlocked("network access blocked by tests/netblock")


socket.socket.connect = _blocked
socket.socket.connect_ex = _blocked
socket.create_connection = _blocked
socket.getaddrinfo = _blocked
socket.gethostbyname = _blocked
