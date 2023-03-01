from io import BytesIO
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

from data import Text
from keyboards import cancel, menu
from loader import dp, logger
from states import AddClient
from wireguard_api_handler import APIHandler
import qrcode


def put_bytes_to_file(file: bytes) -> BytesIO:
    bytes_file = BytesIO(file)
    bytes_file.seek(0)
    return bytes_file


@dp.callback_query_handler(text="cancel", state=AddClient)
async def cancel_order(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(Text.MENU, reply_markup=menu)
    await call.answer()
    await state.finish()


@dp.callback_query_handler(text_contains="add_client")
async def ask_peer_name_handler(call: CallbackQuery, state: FSMContext):

    cancel_menu = InlineKeyboardMarkup()
    cancel_menu.insert(cancel)
    await call.message.edit_text(Text.ASK_NAME, reply_markup=cancel_menu)
    await call.answer()
    await AddClient.name.set()


@dp.message_handler(state=AddClient.name)
async def create_peer_handler(message: Message, state: FSMContext):
    peer_name = message.text

    handler = APIHandler()
    await handler.create_peer(peer_name)
    peer_config = await handler.get_peer(peer_name)

    image = qrcode.make(peer_config)
    bytes_array = BytesIO()
    image.save(bytes_array, format="PNG")
    photo_data = bytes_array.getvalue()
    photo = put_bytes_to_file(photo_data)
    photo.name = peer_name + ".png"
    await message.reply(Text.CLIENT_ADDED.format(client_name=peer_name))
    await message.answer_photo(photo=photo)
    logger.info(f"added client {peer_name} from user {message.from_user.username}:{message.from_user.id}")

    await message.answer(Text.MENU, reply_markup=menu)
    await state.finish()
