import time

from aiogram.types import CallbackQuery

from handlers.pagination_message_editor import redis_data

async def clear_history_output(request):
    if isinstance(request, CallbackQuery):
        message_object = request.message
    else:
        message_object = request

    message_one = await redis_data.get_data(
        key=str(message_object.from_user.id) + ':first_in_last_stack')
    message_two = await redis_data.get_data(
            key=str(message_object.from_user.id) + ':second_in_last_stack')

    if message_one and message_two:
        for message in (message_one, message_two):
            await message_object.bot.delete_message(chat_id=message_object.chat.id, message_id=message)
            time.sleep(0.25)

        await redis_data.set_data(str(message_object.from_user.id) + ':first_in_last_stack', 0)
        await redis_data.set_data(str(message_object.from_user.id) + ':second_in_last_stack', 0)
