from asyncio import subprocess
from sqlalchemy.exc import IntegrityError

from wireguard.config import WG_ID
from wireguard.wireguard_config.client import ClientCreator
from wireguard.wireguard_config.client_config import render as render_client_config
from wireguard.api.exceptions import ClientNotExistsError, ClientAlreadyExistsError
from wireguard.loader import db_api as db
from wireguard.database.models import Client
from wireguard.wireguard_config.wireguard_server_api import write_config_and_reload_server


async def create_client(username: str):
    client_creator = ClientCreator(username)
    try:
        await db.insert_new_client(client_creator.create())
        await write_config_and_reload_server()
    except IntegrityError:
        raise ClientAlreadyExistsError


async def get_client_config(username: str) -> str:
    data = await db.select_client(username)
    if not data:
        raise ClientNotExistsError
    client: Client = await db.select_client(username)
    return render_client_config(client)


async def delete_client(username: str):
    client: Client = await db.delete_client(username)
    if not client:
        raise ClientNotExistsError
    await write_config_and_reload_server()


async def get_active_clients_names() -> list[str]:
    return await db.select_all_active_clients_names()


async def get_client_latest_handshake_timestamp(username: str) -> int:
    client = await db.select_client(username)

    if not client:
        raise ClientNotExistsError

    process: subprocess.Process = await subprocess.create_subprocess_shell(f"wg show {WG_ID} latest-handshakes", stdout=subprocess.PIPE)

    result = (await process.stdout.read()).decode().strip()

    if not result:
        raise ClientNotExistsError

    for row in result.split("\n"):
        publickey, timestamp = row.split()

        if publickey == client.publickey:
            return int(timestamp)
    raise ClientNotExistsError


async def get_client_traffic(username: str) -> tuple[int, int]:
    client = await db.select_client(username)

    if not client:
        raise ClientNotExistsError

    process: subprocess.Process = await subprocess.create_subprocess_shell(f"wg show {WG_ID} transfer", stdout=subprocess.PIPE)

    result = (await process.stdout.read()).decode().strip()

    if not result:
        raise ClientNotExistsError

    for row in result.split("\n"):
        publickey, received_bytes, sent_bytes = row.split()

        if publickey == client.publickey:
            return int(received_bytes), int(sent_bytes)
    raise ClientNotExistsError


async def get_client_received_bytes(username: str) -> int:
    return (await get_client_traffic(username))[0]


async def get_client_sent_bytes(username: str) -> int:
    return (await get_client_traffic(username))[1]



