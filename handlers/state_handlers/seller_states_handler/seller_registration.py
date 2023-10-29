import importlib
import phonenumbers
from typing import Union
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram import Bot


from handlers.state_handlers.buyer_registration_handlers import registartion_view_corrector
from states.seller_registration_states import HybridSellerRegistrationStates, PersonSellerRegistrationStates, CarDealerShipRegistrationStates


async def input_seller_name(request: Union[CallbackQuery, Message], state: FSMContext, incorrect = False):
    message_editor_module = importlib.import_module('handlers.message_editor')
    redis_module = importlib.import_module('handlers.default_handlers.start')  # Ленивый импорт

    seller_mode = await redis_module.redis_data.get_data(key=str(request.from_user.id) + ':seller_registration_mode')
    print('seller_mode', seller_mode)

    if str(await state.get_state()) != 'PersonSellerRegistrationStates:input_fullname':
        await state.set_state(PersonSellerRegistrationStates.input_fullname)

    if isinstance(request, CallbackQuery):
        request = request.message
    elif isinstance(request, Message):
        pass
    


    if incorrect:
        await state.update_data(incorrect_answer=True)
        if seller_mode == 'dealership':
            lexicon_code = 'write_dealership_name(incorrect)'
        elif seller_mode == 'person':
            lexicon_code = 'write_full_seller_name(incorrect)'

        message_reply_mode = True
        print('reply_mode1')
        delete_last_message_mode = True

            
        await registartion_view_corrector(request=request, state=state)
        

        await redis_module.redis_data.set_data(
            key=str(request.from_user.id) + ':last_user_message',
            value=request.message_id)

    else:
        print(seller_mode)
        if seller_mode == 'dealership':
            
            lexicon_code = 'write_dealership_name'
            print('lexdeal', lexicon_code)
        elif seller_mode == 'person':
            lexicon_code = 'write_full_seller_name'
            

        message_reply_mode = False
        delete_last_message_mode = False

    print('start_editor_with', lexicon_code)
    await message_editor_module.travel_editor.edit_message(request=request, lexicon_key=lexicon_code, lexicon_cache=False,
                                                            reply_mode=message_reply_mode)

    await state.set_state(HybridSellerRegistrationStates.input_number)
    

#Фильтр CorrectName()
async def hybrid_input_seller_number(request: Union[CallbackQuery, Message], state: FSMContext, user_name=None, incorrect = False):
    message_editor_module = importlib.import_module('handlers.message_editor')
    redis_module = importlib.import_module('handlers.default_handlers.start')  # Ленивый импорт
    
    await state.update_data(seller_person_name=user_name)

    if isinstance(request, CallbackQuery):
        request = request.message
    elif isinstance(request, Message):
        pass
    
    bot = request.chat.bot

    if incorrect:
        await state.update_data(incorrect_answer=True)
        lexicon_code = 'write_seller_phone_number(incorrect)'
        message_reply_mode = True
        print('reply_mode1')
        delete_last_message_mode = True

        await registartion_view_corrector(request=request, state=state)
        
        

        await redis_module.redis_data.set_data(
            key=str(request.from_user.id) + ':last_user_message',
            value=request.message_id)
        
    else:
        redis_key = str(request.from_user.id) + ':last_user_message'
        last_user_message = await redis_module.redis_data.get_data(key=redis_key)
        if last_user_message:
            await bot.delete_message(chat_id=request.chat.id, message_id=last_user_message)
            await redis_module.redis_data.delete_key(key=redis_key)
        await bot.delete_message(chat_id=request.chat.id, message_id = request.message_id)
        lexicon_code = 'write_seller_phone_number'
        message_reply_mode = False
        delete_last_message_mode = False

    await message_editor_module.travel_editor.edit_message(request=request, lexicon_key=lexicon_code,
                                                             lexicon_cache=False, 
                                                             reply_mode = message_reply_mode)
    
    await state.set_state(HybridSellerRegistrationStates.check_input_number)


#Фильтр CorrectNumber
async def check_your_config(message: Message, state: FSMContext, input_number=None, person=True, dealership=False):
    bot = message.chat.bot
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.update_data(seller_number=input_number)
    memory_storage = await state.get_data()
    await registartion_view_corrector(request=message, state=state)
    
    await message.answer('final anal')

    #person=True
    if person:
        person_fullname = memory_storage.get('seller_person_name')
        person_number = input_number

    elif dealership:
        dealership_name = memory_storage.get('dealership_name')
        dealership_number = memory_storage.get('dealership_number')
        

    

    