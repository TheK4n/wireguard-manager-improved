import asyncio

import os
import sys
import jinja2

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(PROJECT_ROOT)

from wireguard.config import WG_SERVER_PRIVATEKEY, WG_PORT, WG_CONFIGFILE
from wireguard.loader import db_main as db


config_template = r"""
[Interface]
PrivateKey = {{ server_privatekey }}
Address = 10.0.0.1/24
ListenPort = {{ server_port }}
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0+ -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0+ -j MASQUERADE


{% for client in clients %}
[Peer]
PublicKey = {{ client.publickey }}
{% if client.presharedkey %}
PresharedKey = {{ client.presharedkey }}
{% endif %}
AllowedIPs = {{ client.addr4 }}/32
{% endfor %}
"""


async def render() -> str:
    data = {
            "server_privatekey": WG_SERVER_PRIVATEKEY,
            "server_port": WG_PORT
            }
    env = jinja2.Environment(trim_blocks=True)
    tmpl = env.from_string(config_template)

    clients = await db.select_all_active_clients()
    return tmpl.render(**data, clients=clients)



async def generate_and_write_config():
    with open(WG_CONFIGFILE, "w") as f:
        f.write(await render())


if __name__ == '__main__':
    asyncio.run(generate_and_write_config())

