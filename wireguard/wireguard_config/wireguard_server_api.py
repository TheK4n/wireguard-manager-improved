from asyncio import subprocess
from wireguard.config import WG_ID
from wireguard.loader import logger
from wireguard.wireguard_config.server_config import generate_and_write_config



TEMP_CONF_FILENAME = "/tmp/.wg_stripped_config.conf"


async def get_stripped_config() -> str:
    proc = await subprocess.create_subprocess_shell(
        f"wg-quick strip {WG_ID}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, _ = await proc.communicate()

    return stdout.decode()


async def write_temp_conf(stripped_config: str):
    with open(TEMP_CONF_FILENAME, "w") as f:
        f.write(stripped_config)


async def sync_config() -> int:
    proc = await subprocess.create_subprocess_shell(
        f"wg syncconf {WG_ID} {TEMP_CONF_FILENAME}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    await proc.communicate()

    return proc.returncode if proc.returncode else 0


async def reload_server():
    await write_temp_conf(await get_stripped_config())
    return_code = await sync_config()
    if return_code != 0:
        logger.error("reload server")


async def write_config_and_reload_server():
    await generate_and_write_config()
    await reload_server()

