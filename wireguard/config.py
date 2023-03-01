import urllib.request
from environs import Env


env = Env()
env.read_env()


GLOBAL_IP = env.str("GLOBAL_IP", 
                    default=urllib.request.urlopen('https://ident.me').read().decode())

WG_PORT = env.int("WG_PORT",
                  default=51830,
                  validate=lambda port: 1023 < port < 65536,
                  error="Port must be in range from 1024 to 65535")


with env.prefixed("POSTGRES_"):
    DB_USER = env.str("USER", default="postgres")
    DB_PASSWORD = env.str("PASSWORD")
    DB_HOST = env.str("HOST")
    DB_PORT = env.int("PORT", default=5432)
    DB_NAME = env.str("DATABASE_NAME", default="postgres")


WG_ID = "wg0"
WG_PREFIX = "/etc/wireguard"
WG_CONFIGFILE = f"{WG_PREFIX}/{WG_ID}.conf"
WG_SERVER_PRIVATEKEY = open(f"{WG_PREFIX}/data/priv.key").read().strip()
WG_SERVER_PUBLICKEY = open(f"{WG_PREFIX}/data/pub.key").read().strip()

CLIENT_DNSs = "208.67.222.222,208.67.220.220"


CLIENT_USERNAME_MAX_LENGTH = 70
CLIENT_USERNAME_MIN_LENGTH = 3

API_HOST = "0.0.0.0"
API_PORT = 8080

