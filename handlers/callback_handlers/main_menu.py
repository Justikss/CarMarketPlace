import importlib
from typing import Union


from aiogram.types import CallbackQuery, Message




async def main_menu(request: Union[CallbackQuery, Message]):
    message_editor = importlib.import_module('handlers.message_editor')  # Ленивый импорт

    await message_editor.travel_editor.edit_message(lexicon_key='main_menu', request=request)
# =======
# from handlers.handler_utils.output_clear_offers_history import clear_history_output
# from handlers.message_editor import travel_editor
# from handlers.callback_handlers.search_auto_handler import redis_data

# async def main_menu(request: Union[CallbackQuery, Message]):
#     await clear_history_output(request)

#     await travel_editor.edit_message(lexicon_key='main_menu', request=request, delete_mode=True)
# >>>>>>> main-bot
    user_id = request.from_user.id
    # redis_key = str(user_id) + ':last_lexicon_code'
    # await message_editor.redis_data.set_data(redis_key, 'main_menu')

