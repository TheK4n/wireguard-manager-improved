import jinja2
from wireguard.config import GLOBAL_IP, WG_PORT, WG_SERVER_PUBLICKEY, CLIENT_DNSs
from wireguard.wireguard_config.models import Client


config_template = r"""[Interface]
PrivateKey = {{ client.privatekey }}
Address = {{ client.addr4 }}/32
DNS = {{ DNSs }}

[Peer]
PublicKey = {{ server_publickey }}
{% if client.presharedkey %}
PresharedKey = {{ client.presharedkey }}
{% endif %}
Endpoint = {{ server_global_ip }}:{{ server_port }}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""



def render(client: Client) -> str:
    data = {
            "server_publickey": WG_SERVER_PUBLICKEY,
            "server_port": WG_PORT,
            "server_global_ip": GLOBAL_IP,
            "DNSs": CLIENT_DNSs
        }

    env = jinja2.Environment(trim_blocks=True)
    tmpl = env.from_string(config_template)

    return tmpl.render(**data, client=client)


