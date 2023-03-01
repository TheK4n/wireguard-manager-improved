#!/usr/bin/env python3

if __name__ != '__main__':
    exit()


import os
import sys
import uvicorn
import sys



PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(PROJECT_ROOT)


if len(sys.argv) < 2:
    exit(1)


match sys.argv[1]:
    case "generate_config":
        import asyncio
        from wireguard.wireguard_config.server_config import generate_and_write_config
        asyncio.run(generate_and_write_config())
        exit(0)

    case "initialize_database":
        import asyncio
        from wireguard.loader import db_main as db
        asyncio.run(db.create_and_populate_tables())
        exit(0)

    case "run":
        from wireguard.api.api import app
        from wireguard.config import API_HOST, API_PORT
        uvicorn.run(app, host=API_HOST, port=API_PORT)

    case _:
        print("manager.py (generate_config, initialize_database, run)", file=sys.stderr)
        exit(1)

