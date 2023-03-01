from fastapi import FastAPI, APIRouter, Body, HTTPException, status, Path, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response


from wireguard.api.clients import (
    create_client, get_client_config, delete_client,
    get_active_clients_names, get_client_latest_handshake_timestamp,
    get_client_received_bytes, get_client_sent_bytes,
)

from wireguard.api.exceptions import ClientNotExistsError, ClientAlreadyExistsError
from wireguard import config
from wireguard.loader import logger


app = FastAPI()
clients_router = APIRouter(prefix="/clients")


@clients_router.options("", status_code=status.HTTP_200_OK)
async def options_request_view():
    headers = {"Allow": "GET, POST, DELETE"}
    return Response(headers=headers)


@clients_router.get("", status_code=status.HTTP_200_OK)
async def get_all_active_clients_view():
    clients_names: list[str] = await get_active_clients_names()
    return JSONResponse(clients_names)

options = {
    "title": "Username of client",
    "min_length": config.CLIENT_USERNAME_MIN_LENGTH,
    "max_length": config.CLIENT_USERNAME_MAX_LENGTH,
    "regex": r'^[a-zA-z0-9_]{3,}$'
}
CustomPath: str = Path(**options)
CustomBody: str = Body(embed=True, **options)


@clients_router.get("/{username}", status_code=status.HTTP_200_OK)
async def get_client_data_view(username: str = CustomPath):

    try:
        data = await get_client_config(username)
        logger.info(f"get config of client '{username}'")
    except ClientNotExistsError:
        responce = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Client '{username}' not exists")
        logger.warn(f"client '{username}' not exists")
    else:
        responce = PlainTextResponse(data)
    return responce


@clients_router.get("/{username}/latest-handshake", status_code=status.HTTP_200_OK)
async def get_client_latest_handshake_view(username: str = CustomPath):
    timestamp: int = await get_client_latest_handshake_timestamp(username)
    return JSONResponse(timestamp)


@clients_router.get("/{username}/traffic-received", status_code=status.HTTP_200_OK)
async def get_client_traffic_received_bytes_view(username: str = CustomPath):
    bytes_number: int = await get_client_received_bytes(username)
    return JSONResponse(bytes_number)


@clients_router.get("/{username}/traffic-sent", status_code=status.HTTP_200_OK)
async def get_client_traffic_sent_bytes_view(username: str = CustomPath):
    bytes_number: int = await get_client_sent_bytes(username)
    return JSONResponse(bytes_number)


@clients_router.post("", status_code=status.HTTP_201_CREATED)
async def create_client_view(request: Request, username: str = CustomBody):
    try:
        await create_client(username.strip())
        logger.info(f"client '{username}' was created")
    except ClientAlreadyExistsError:
        responce = HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"client '{username}' already exists")
        logger.warn(f"client '{username}' already exists")
    else:
        headers = {"Location": f"{request.headers['host']}/clients/{username}"}
        responce = Response(headers=headers, status_code=status.HTTP_201_CREATED)
    return responce


@clients_router.delete("/{username}")
async def delete_client_view(username: str = CustomPath):
    try:
        await delete_client(username)
        logger.info(f"client '{username}' was deleted")
    except ClientNotExistsError:
        logger.warn(f"client '{username}' not exists")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


app.include_router(clients_router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
