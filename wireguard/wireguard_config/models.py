
from typing import NamedTuple


class Client(NamedTuple):
    name: str | None = None
    privatekey: str | None = None
    publickey: str | None = None
    presharedkey: str | None = None
    addr4: str | None = None
    addr6: str | None = None

