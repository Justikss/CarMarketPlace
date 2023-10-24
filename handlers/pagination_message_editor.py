from typing import Union

from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.state_handlers.choose_car_for_buy.hybrid_handlers import InlineCreator
from handlers.state_handlers.choose_car_for_buy.choose_car_utils.output_chosen_search_config import redis_data
from utils.Lexicon import LEXICON


async def paginaton_message_editor(request: Union[CallbackQuery, Message], lexicon_code=None, message_stack: list = None,
                                   delete_mode=False):

    if isinstance(request, CallbackQuery):
        message_object = request.message
    else:
        message_object = request

    redis_key = str(message_object.from_user.id) + ':pagination_code'
    pagination_code = await redis_data.get_data(redis_key)
    if not pagination_code:
        pagination_code = 0

    if lexicon_code:
        lexicon_part = LEXICON.get(lexicon_code)
        if message_stack:
            if pagination_code < len(message_stack) - 3:
                message_part = message_stack[pagination_code:pagination_code+3]
                await redis_data.set_data(redis_key, pagination_code+3)
                if pagination_code == 0:
                    buttons = [[InlineKeyboardButton(text=caption, callback_data=data)]
                               for data, caption in lexicon_part.items() if data != 'left_vector']
                else:
                    buttons = [[InlineKeyboardButton(text=caption, callback_data=data)]
                               for data, caption in lexicon_part.items()]


            else:
                message_part = message_stack[pagination_code:]
                await redis_data.set_data(redis_key, 0)
                buttons = [[InlineKeyboardButton(text=caption, callback_data=data)]
                           for data, caption in lexicon_part.items() if data != 'right_vector']

            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

            print(message_stack)
            # message_stack = message_part[3:]
            # print(message_stack)
            if delete_mode:
                last_message = await redis_data.get_data(str(message_object.from_user.id) + ':last_message')
                message_object.chat.delete_message(self=message_object.chat, message_id=last_message)


                for message in message_part:
                    if message_part.index(message) != 2:
                        message_id = await message_object.answer(text=message)
                        if message_part.index(message) == 0:
                            await redis_data.set_data(key=str(message_object.from_user.id) + ':first_in_last_stack',
                                                      value=message_id.message_id)
                        elif message_part.index(message) == 1:
                            await redis_data.set_data(key=str(message_object.from_user.id) + ':second_in_last_stack',
                                                      value=message_id.message_id)
                    else:
                        message_id = await message_object.answer(text=message, reply_markup=keyboard)
                        await redis_data.set_data(key=str(message_object.from_user.id) + ':third_in_last_stack',
                                                  value=message_id.message_id)

            else:
                for message in message_part:
                    if message_part.index(message) != 2:
                        if message_part.index(message) == 0:
                            message_id = await redis_data.get_data(
                                key=str(message_object.from_user.id) + ':first_in_last_stack')

                        elif message_part.index(message) == 1:
                            message_id = await redis_data.get_data(
                                key=str(message_object.from_user.id) + ':second_in_last_stack')

                        await message_object.chat.bot.edit_message_text(self=message_object.chat,
                                                                        chat_id=message_object.chat.id,
                                                                        message_id=message_id,
                                                                        text=message)

                    else:
                        message_id = await redis_data.get_data(
                            key=str(message_object.from_user.id) + ':third_in_last_stack')

                        await message_object.chat.bot.edit_message_text(self=message_object.chat,
                                                                        chat_id=message_object.chat.id,
                                                                        message_id=message_id,
                                                                        text=message, reply_markup=keyboard)




        else:
            pass



async def left_vector_pagination_handler(callback: CallbackQuery):
    redis_key = str(callback.from_user.id) + ':pagination_code'
    pagination_code = await redis_data.get_data(redis_key)
    await redis_data.set_data(redis_key, pagination_code - 3)
    await paginaton_message_editor(request=callback, lexicon_code='buttons_offers_history_for_buyer_output')

async def right_vector_pagination_handler(callback: CallbackQuery):
    redis_key = str(callback.from_user.id) + ':pagination_code'
    pagination_code = await redis_data.get_data(redis_key)
    await redis_data.set_data(redis_key, pagination_code + 3)
    await paginaton_message_editor(request=callback, lexicon_code='buttons_offers_history_for_buyer_output')
