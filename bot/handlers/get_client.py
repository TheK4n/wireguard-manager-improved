import math
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from data import Text, ButtonText
from keyboards import cancel, menu
from loader import dp, logger
from states import GetClient
from io import BytesIO
import qrcode
from wireguard_api_handler import APIHandler


NUMBER_OF_CLIENTS_ON_PAGE = 6


def raw_to_html(raw: str) -> str:
    res = ''
    for i in raw.split("\n"):
        pre = i.split(" = ")
        try:
            if pre[0] in ("PrivateKey", "PresharedKey"):
                res += f"{pre[0]} = <span class=\"tg-spoiler\">{pre[1]}</span>\n"
            else:
                res += f"{pre[0]} = <code>{pre[1]}</code>\n"
        except IndexError:
            res += i + "\n"
    return res.strip()


def put_bytes_to_file(data: bytes) -> BytesIO:
    bytes_file = BytesIO(data)
    bytes_file.seek(0)
    return bytes_file


def get_clients_with_offset(clients: list[str], page: int):
    offset = NUMBER_OF_CLIENTS_ON_PAGE * page
    print(clients)
    res = clients[offset:NUMBER_OF_CLIENTS_ON_PAGE + offset]
    return res


def fill_blank_with_spaces(clients: list[str]) -> list[str]:
    res = clients.copy()
    for _ in range(NUMBER_OF_CLIENTS_ON_PAGE - len(res)):
        res.append(" "  * 20)
    return res


@dp.callback_query_handler(text_contains="cancel", state=GetClient)
async def cancel_order(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(Text.MENU, reply_markup=menu)
    await call.answer()
    await state.finish()


@dp.callback_query_handler(text_contains="cancel")
async def cancel_order2(call: CallbackQuery):
    await call.message.edit_text(Text.MENU, reply_markup=menu)
    await call.answer()


@dp.callback_query_handler(text="_")
async def plug(call: CallbackQuery):
    await call.answer()


@dp.callback_query_handler(text_contains="clients")
async def get_client(call: CallbackQuery, state: FSMContext):
    page = int(call.data.split(":")[1])

    handler = APIHandler()
    all_clients = await handler.get_active_peers()

    total_pages = math.ceil(len(all_clients) / NUMBER_OF_CLIENTS_ON_PAGE)

    if page >= total_pages:
        page = 0

    if page < 0:
        page = total_pages - 1

    clients = fill_blank_with_spaces(get_clients_with_offset(all_clients, page))

    clients_keyboard = InlineKeyboardMarkup()
    for client_name in clients:
        if client_name == " " * 20:
            clients_keyboard.insert(InlineKeyboardButton(text=client_name, callback_data=f'_'))
        else:
            clients_keyboard.insert(InlineKeyboardButton(text=client_name, callback_data=f'client_name:{client_name}:{page}'))

    prev_page_button = InlineKeyboardButton(text="<", callback_data=f"clients:{page - 1}")
    current_page_button = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="_")
    next_page_button = InlineKeyboardButton(text=">", callback_data=f"clients:{page + 1}")

    clients_keyboard.row(prev_page_button, current_page_button, next_page_button)
    clients_keyboard.row(cancel)

    await call.message.edit_text(Text.CLIENTS, reply_markup=clients_keyboard)
    await call.answer()


@dp.callback_query_handler(text_contains="client_name")
async def get_client_2(call: CallbackQuery, state: FSMContext):
    client_name = call.data.split(':')[1]
    page = call.data.split(':')[2]

    get_client_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=ButtonText.GET_QR, callback_data=f'get_client_get_name:get_qrcode:{client_name}'),
                InlineKeyboardButton(text=ButtonText.GET_FILE, callback_data=f'get_client_get_name:get_file:{client_name}'),
            ],
            [
                InlineKeyboardButton(text=ButtonText.GET_RAW, callback_data=f"get_client_get_name:get_raw:{client_name}"),
            ],
            [
                InlineKeyboardButton(text=ButtonText.DELETE, callback_data=f"get_client_get_name:delete:{client_name}"),
            ],
            [
                InlineKeyboardButton(text=ButtonText.BACK_MENU, callback_data=f"clients:{page}")
            ]
        ]
    )

    await call.message.edit_text(Text.CLIENT.format(client_name=client_name), reply_markup=get_client_menu)
    await call.answer()


@dp.callback_query_handler(text_contains="get_client_get_name")
async def get_client_3(call: CallbackQuery, state: FSMContext):
    _, command, client_name = call.data.split(":")
    handler = APIHandler()

    if command == "get_qrcode":
        config_raw = await handler.get_peer(client_name)
        image = qrcode.make(config_raw)
        bytes_array = BytesIO()
        image.save(bytes_array, format="PNG")
        photo_data = bytes_array.getvalue()
        photo = put_bytes_to_file(photo_data)
        photo.name = client_name + ".png"
        await call.message.answer_photo(photo=photo)
        await call.answer()
        logger.info(f"get qrcode \"{client_name}\" from user {call.from_user.username}:{call.from_user.id}")
    elif command == "get_file":
        config_raw = await handler.get_peer(client_name)
        document = put_bytes_to_file(config_raw.encode())
        document.name = client_name + ".conf"
        await call.message.answer_document(document=document)
        await call.answer()
        logger.info(f"get file \"{client_name}\" from user {call.from_user.username}:{call.from_user.id}")
    elif command == "get_raw":
        config_raw = await handler.get_peer(client_name)
        await call.message.answer(raw_to_html(config_raw), parse_mode="html")
        await call.answer()
        logger.info(f"get raw \"{client_name}\" from user {call.from_user.username}:{call.from_user.id}")
    elif command == "delete":
        conf_del = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=ButtonText.CONFIRM, callback_data=f"confirm:{client_name}")
                ],
                [
                    InlineKeyboardButton(text=ButtonText.BACK_MENU, callback_data="cancel:_")
                ],
            ]
        )
        await call.answer()
        await call.message.edit_text(Text.CLIENT_DELETE_CONFIRM.format(client_name=client_name), reply_markup=conf_del)
        await GetClient.name.set()


@dp.callback_query_handler(state=GetClient.name)
async def get_client_4(call: CallbackQuery, state: FSMContext):
    _, client_name = call.data.split(":")
    handler = APIHandler()
    await handler.delete_peer(client_name)
    await call.message.edit_text(Text.CLIENT_DELETED.format(client_name=client_name), reply_markup=menu)
    await call.answer()
    await state.finish()
    logger.info(f"deleted client \"{client_name}\" from user {call.from_user.username}:{call.from_user.id}")

