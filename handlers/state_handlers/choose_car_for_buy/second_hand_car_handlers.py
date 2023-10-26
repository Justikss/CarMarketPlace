import importlib

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


from database.data_requests.commodity_requests import CommodityRequester, cars
from database.data_requests.person_requests import buyer, sellers
from database.tables.offers_history import ActiveOffers

from states.hybrid_choose_states import HybridChooseStates
from states.second_hand_choose_states import SecondHandChooseStates
from handlers.state_handlers.choose_car_for_buy.new_car_handlers import cache_state

# ActiveOffers.create(seller=sellers[0], buyer=buyer[0], car=cars[0])
# ActiveOffers.create(seller=sellers[0], buyer=buyer[0], car=cars[3])
# ActiveOffers.create(seller=sellers[0], buyer=buyer[0], car=cars[1])
# ActiveOffers.create(seller=sellers[0], buyer=buyer[0], car=cars[2])


async def choose_color_handler(callback: CallbackQuery, state: FSMContext, first_call=True):
    print('pre-true')
    message_editor = importlib.import_module('handlers.message_editor')  # Ленивый импорт

    await cache_state(callback=callback, state=state)

    memory_storage = await state.get_data()
    if first_call:
        user_answer = callback.data.split(':')[1]  # Второе слово - ключевое к значению бд
        await state.update_data(cars_complectation=user_answer)
    else:
        user_answer = memory_storage['cars_complectation']
    models_range = CommodityRequester.get_for_request(state=memory_storage['cars_state'],
                                                      brand=memory_storage['cars_brand'],
                                                      model=memory_storage['cars_model'],
                                                      engine_type=memory_storage['cars_engine_type'],
                                                      complectation=user_answer,
                                                      )

    button_texts = {car.color for car in models_range}
    await message_editor.travel_editor.edit_message(request=callback, lexicon_key='choose_color', button_texts=button_texts,
                                     callback_sign='cars_color:', lexicon_cache=False)

    await state.set_state(SecondHandChooseStates.select_mileage)


async def choose_mileage_handler(callback: CallbackQuery, state: FSMContext, first_call=True):
    message_editor = importlib.import_module('handlers.message_editor')  # Ленивый импорт

    await cache_state(callback=callback, state=state)

    memory_storage = await state.get_data()
    if first_call:
        user_answer = callback.data.split(':')[1]  # Второе слово - ключевое к значению бд
        await state.update_data(cars_color=user_answer)
    else:
        user_answer = memory_storage['cars_color']
    models_range = CommodityRequester.get_for_request(state=memory_storage['cars_state'],
                                                      brand=memory_storage['cars_brand'],
                                                      model=memory_storage['cars_model'],
                                                      engine_type=memory_storage['cars_engine_type'],
                                                      complectation=memory_storage['cars_complectation'],
                                                      color=user_answer)

    button_texts = {str(car.mileage) for car in models_range}
    await message_editor.travel_editor.edit_message(request=callback, lexicon_key='choose_mileage', button_texts=button_texts,
                                     callback_sign='cars_mileage:', lexicon_cache=False)

    await state.set_state(SecondHandChooseStates.select_year)



async def choose_year_of_release_handler(callback: CallbackQuery, state: FSMContext, first_call=True):
    message_editor = importlib.import_module('handlers.message_editor')  # Ленивый импорт

    await cache_state(callback=callback, state=state)

    memory_storage = await state.get_data()
    if first_call:
        user_answer = callback.data.split(':')[1]  # Второе слово - ключевое к значению бд
        await state.update_data(cars_mileage=user_answer)
    else:
        user_answer = memory_storage['cars_mileage']
    models_range = CommodityRequester.get_for_request(state=memory_storage['cars_state'],
                                                      brand=memory_storage['cars_brand'],
                                                      model=memory_storage['cars_model'],
                                                      engine_type=memory_storage['cars_engine_type'],
                                                      complectation=memory_storage['cars_complectation'],
                                                      color=memory_storage['cars_color'],
                                                      mileage=user_answer)

    button_texts = {car.year_of_release for car in models_range}
    await message_editor.travel_editor.edit_message(request=callback, lexicon_key='choose_year_of_release', button_texts=button_texts,
                                     callback_sign='cars_year_of_release:', lexicon_cache=False)

    await state.set_state(HybridChooseStates.config_output)


