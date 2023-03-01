import logging
from wireguard.database import DBApi, DBMain
from wireguard.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME


logger = logging.getLogger(__name__)

db_api = DBApi(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
db_main = DBMain(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)


__all__ = ["db_api", "db_main", "logger"]

