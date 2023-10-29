import importlib
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from typing import Union

from database.data_requests.person_requests import PersonRequester

async def load_seller_in_database(request: Union[CallbackQuery, Message], state: FSMContext, authorized_state: bool):
    '''Метод подготовки аргументов(данных продавца) к загрузке в базу данных'''

    redis_module = importlib.import_module('handlers.default_handlers.start')  # Ленивый импорт
    seller_mode = await redis_module.redis_data.get_data(key=str(request.from_user.id) + ':seller_registration_mode')
    memory_storage = await state.get_data()
    formatted_load_pattern = dict()
    user_id = request.from_user.id

    if seller_mode == 'dealership':
        formatted_load_pattern = {
            'telegram_id': user_id,
            'phone_number': memory_storage['seller_number'],
            'dealship_name': memory_storage['seller_name'],
            'entity': 'legal',
            'dealship_address': None,
            'name': None,
            'surname': None,
            'patronymic': None,
            'authorized': authorized_state
        }
    elif seller_mode == 'person':
        person_full_name = memory_storage['seller_name'].split(' ')
        
        if len(person_full_name) == 3:
            patronymic = person_full_name[2]
        elif len(person_full_name) == 2:
            patronymic = None
        name = person_full_name[1]
        surname = person_full_name[0]

        formatted_load_pattern = {
            'telegram_id': user_id,
            'phone_number': memory_storage['seller_number'],
            'dealship_name': None,
            'entity': 'natural',
            'dealship_address': None,
            'name': name,
            'surname': surname,
            'patronymic': patronymic,
            'authorized': authorized_state
        }

    try_load = await PersonRequester.store_data([formatted_load_pattern], seller=True)
    if try_load:
        return True
    else:
        return False