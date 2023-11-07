# import aioredis
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter, and_f, or_f
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.redis import Redis, RedisStorage

from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
'''РАЗДЕЛЕНИЕ НА БИБЛИОТЕКИ(/\) И КАСТОМНЫЕ МОДУЛИ(V)'''

from config_data.config import BOT_TOKEN
from database.tables.offers_history import ActiveOffers, ActiveOffersToCars
from handlers.callback_handlers.buy_part import FAQ_tech_support, backward_callback_handler, callback_handler_backward_in_carpooling, callback_handler_start_buy, confirm_from_seller_callback_handler, confirm_search_config, language_callback_handler, main_menu, search_auto_handler, show_offers_history
from handlers.custom_filters import correct_name, correct_number, pass_on_dealership_address, price_is_digit, message_is_photo
from handlers.default_handlers import start, help, echo
from handlers.callback_handlers.buy_part import (return_main_menu_from_offers_history)
from handlers.state_handlers import buyer_registration_handlers
from handlers.state_handlers.buyer_registration_handlers import BuyerRegistationStates
from handlers.state_handlers.choose_car_for_buy import hybrid_handlers, new_car_handlers, second_hand_car_handlers

from states.new_car_choose_states import NewCarChooseStates
from states.hybrid_choose_states import HybridChooseStates
from states.second_hand_choose_states import SecondHandChooseStates
from states.load_commodity_states import LoadCommodityStates
from states.tariffs_to_seller import ChoiceTariffForSellerStates

from states.seller_registration_states import HybridSellerRegistrationStates, CarDealerShipRegistrationStates
from handlers.callback_handlers.sell_part import start_sell_button_handler, start_seller_registration_callback_handlers, accept_registration_request_button, seller_faq, commodity_requests
from handlers.callback_handlers import sell_part
from handlers.state_handlers.seller_states_handler.seller_registration import seller_registration_handlers, await_confirm_from_admin, check_your_registration_config
from handlers.state_handlers.seller_states_handler import load_new_car

from handlers.state_handlers.seller_states_handler import seller_profile_branch


from handlers.callback_handlers.hybrid_part import return_main_menu




# from database.data_requests.offers_requests import OffersRequester
# from database.data_requests.person_requests import PersonRequester

# a = OffersRequester.store_data(buyer_id=902230076, seller_id=902230076, cars=[1, 2, 5])
# print(a)

# offer = ActiveOffers.get(ActiveOffers.id == 1)
# related_cars = offer.offer_id
# print(type(offer))

#active_offer_to_car = [offer_wire for offer_wire in ActiveOffersToCars.get(ActiveOffersToCars.offer_id == 4)]
# related_offer = active_offer_to_car.offer_id

#print(active_offer_to_car)


'''echo.router обязан последней позици.'''

redis = None
bot = None

redis = Redis(host='localhost')
storage = RedisStorage(redis=redis)

dp = Dispatcher(storage=storage)


async def start_bot():
    global redis, edit_last_message, bot, dp, redis, storage
    bot = Bot(token=BOT_TOKEN)

    redis = Redis(host='localhost')
    storage = RedisStorage(redis=redis)

    dp = Dispatcher(storage=storage)


    '''обраюотка Сообщений'''
    dp.message.register(start.bot_start, Command(commands=["start"], ignore_case=True))
    # dp.message.register(help.bot_help, Command(commands=["help"]))

    '''Состояния ргеистрации покупателя'''
    dp.callback_query.register(buyer_registration_handlers.input_full_name,
                               StateFilter(BuyerRegistationStates.input_full_name))
    dp.message.register(buyer_registration_handlers.input_phone_number,
                        StateFilter(BuyerRegistationStates.input_phone_number), correct_name.CheckInputName())
    dp.message.register(buyer_registration_handlers.finish_check_phone_number,
                        StateFilter(BuyerRegistationStates.finish_check_phone_number))
    '''Состояния регистрации продавцов'''
    dp.callback_query.register(await_confirm_from_admin.seller_await_confirm_by_admin,
                              F.data == 'confirm_registration_from_seller')

    dp.callback_query.register(start_seller_registration_callback_handlers.seller_type_identifier,
                                    F.data.in_(('i_am_private_person', 'i_am_car_dealership')))

    dp.message.register(seller_registration_handlers.hybrid_input_seller_number, 
                        and_f(StateFilter(HybridSellerRegistrationStates.input_number), correct_name.CheckInputName()))

    dp.message.register(seller_registration_handlers.dealership_input_address,
                        and_f(StateFilter(CarDealerShipRegistrationStates.input_dealship_name), correct_number.CheckInputNumber()))



    dp.callback_query.register(seller_registration_handlers.hybrid_input_seller_number, 
                        and_f(StateFilter(HybridSellerRegistrationStates.check_input_data),
                        F.data == 'rewrite_seller_number'))

    dp.callback_query.register(seller_registration_handlers.input_seller_name,
                              and_f(StateFilter(HybridSellerRegistrationStates.check_input_data),
                              F.data == 'rewrite_seller_name'))

    dp.callback_query.register(seller_registration_handlers.dealership_input_address,
                              and_f(StateFilter(HybridSellerRegistrationStates.check_input_data),
                               F.data == 'rewrite_dealership_address'))
    
    dp.message.register(check_your_registration_config.check_your_config,
                        and_f(StateFilter(HybridSellerRegistrationStates.check_input_data),
                        pass_on_dealership_address.GetDealershipAddress()))


      # rewrite_seller_name
      # rewrite_seller_number
      # confirm_registration_from_seller

    '''обработка Коллбэков'''
    # dp.callback_query.register(FAQ_tech_support.testor)
    dp.callback_query.register(FAQ_tech_support.tech_support_callback_handler, F.data == 'support')
    dp.callback_query.register(FAQ_tech_support.write_to_support_callback_handler, F.data == 'write_to_support')
    dp.callback_query.register(FAQ_tech_support.call_to_support_callback_handler, F.data == 'call_to_support')
    dp.callback_query.register(FAQ_tech_support.FAQ_callback_handler, F.data == 'faq')

    dp.callback_query.register(callback_handler_backward_in_carpooling.backward_in_carpooling_handler,
                               F.data == 'backward_in_carpooling')
    dp.callback_query.register(language_callback_handler.set_language,
                               F.data.in_(('language_uz', 'language_ru')))
    dp.callback_query.register(callback_handler_start_buy.start_buy,
                               or_f(F.data == 'start_buy', F.data == 'return_to_sell_zone'))
    dp.callback_query.register(backward_callback_handler.backward_button_handler,
                               lambda callback: callback.data.startswith('backward'))
    dp.callback_query.register(search_auto_handler.search_auto_callback_handler,
                               F.data == 'car_search')
    dp.callback_query.register(search_auto_handler.search_configuration_handler,
                               F.data.in_(('second_hand_cars', 'new_cars')))
    dp.callback_query.register(confirm_search_config.confirm_settings_handler,
                               F.data == 'confirm_buy_settings')

    dp.callback_query.register(confirm_from_seller_callback_handler.confirm_from_seller,
                               lambda callback: callback.data.startswith('confirm_from_seller'))

    dp.callback_query.register(show_offers_history.get_offers_history, F.data == 'offers_to_user')
    dp.callback_query.register(show_offers_history.history_pagination_left, F.data == 'pagination_left')
    dp.callback_query.register(show_offers_history.history_pagination_right, F.data == 'pagination_right')
    dp.callback_query.register(return_main_menu_from_offers_history.return_from_offers_history,
                               F.data == 'return_from_offers_history')

    '''Seller'''
    dp.callback_query.register(start_sell_button_handler.start_sell_callback_handler,
                              or_f(F.data == 'start_sell', F.data == 'return_to_start_seller_registration'))

    dp.callback_query.register(accept_registration_request_button.accept_registraiton,
                        lambda callback: callback.data.startswith('confirm_new_seller_registration_from'))

    dp.callback_query.register(seller_faq.seller_faq, F.data == 'seller_faq')

    dp.callback_query.register(sell_part.commodity_requests.commodity_requests_handler.commodity_reqests_by_seller,
                        F.data == 'create_seller_request')

    dp.callback_query.register(commodity_requests.confirm_load_config_from_seller.confirm_load_config_from_seller,
                              F.data == 'confirm_load_config_from_seller')

    dp.callback_query.register(sell_part.checkout_seller_person_profile.output_seller_profile,
                              F.data == 'seller_pofile')

    '''Оформление тарифа продавца'''
    dp.callback_query.register(seller_profile_branch.tariff_extension.output_affordable_tariffs_handler,
                              and_f(StateFilter(default_state), F.data == 'tariff_extension'))
    dp.callback_query.register(seller_profile_branch.selected_tariff_preview.tariff_preview_handler,
                              and_f(StateFilter(ChoiceTariffForSellerStates.choose_tariff), lambda callback: callback.data.startswith('select_tariff:')))
    dp.callback_query.register(seller_profile_branch.choose_payment.choice_payments_handler,
                              and_f(StateFilter(ChoiceTariffForSellerStates.preview_tariff), F.data == 'start_choose_payment_method'))

    
    

    '''hybrid'''
    
    dp.callback_query.register(return_main_menu.return_main_menu_callback_handler,
                               F.data == 'return_main_menu')

    '''Состояния поиска машины'''
    '''hybrid'''
    dp.callback_query.register(hybrid_handlers.choose_engine_type_handler,
                               and_f(F.data == 'start_configuration_search',
                                     StateFilter(HybridChooseStates.select_engine_type)))
    dp.callback_query.register(hybrid_handlers.choose_brand_handler,
                               and_f(lambda callback: callback.data.startswith('cars_engine_type'),
                                    StateFilter(HybridChooseStates.select_brand)))
    dp.callback_query.register(hybrid_handlers.choose_model_handler,
                               and_f(lambda callback: callback.data.startswith('cars_brand'),
                                     StateFilter(HybridChooseStates.select_model)))
    dp.callback_query.register(hybrid_handlers.choose_complectation_handler,
                               and_f(lambda callback: callback.data.startswith('cars_model'),
                                     StateFilter(HybridChooseStates.select_complectation)))

    dp.callback_query.register(hybrid_handlers.search_config_output_handler,
                               or_f(and_f(lambda callback: callback.data.startswith('cars_year_of_release'),
                                          StateFilter(HybridChooseStates.config_output)),
                                    and_f(lambda callback: callback.data.startswith('cars_complectation'),
                                          StateFilter(HybridChooseStates.config_output))))

    '''new car'''


    '''second hand car'''
    dp.callback_query.register(second_hand_car_handlers.choose_color_handler,
                               and_f(lambda callback: callback.data.startswith('cars_complectation'),
                                     StateFilter(SecondHandChooseStates.select_color)))
    dp.callback_query.register(second_hand_car_handlers.choose_mileage_handler,
                               and_f(lambda callback: callback.data.startswith('cars_color'),
                                     StateFilter(SecondHandChooseStates.select_mileage)))
    dp.callback_query.register(second_hand_car_handlers.choose_year_of_release_handler,
                               and_f(lambda callback: callback.data.startswith('cars_mileage'),
                                     StateFilter(SecondHandChooseStates.select_year)))

    '''Состояния загрузки новых машин'''
    dp.callback_query.register(load_new_car.hybrid_handlers.input_state_to_load,
                              F.data.in_(('create_new_request', 'rewrite_boot_state')))
    dp.callback_query.register(load_new_car.hybrid_handlers.input_engine_type_to_load,
                              or_f(and_f(StateFilter(LoadCommodityStates.input_to_load_engine_type),
                              lambda callback: callback.data.startswith('load_state_')),
                              F.data=='rewrite_boot_engine'))
    dp.callback_query.register(load_new_car.hybrid_handlers.input_brand_to_load,
                              or_f(and_f(StateFilter(LoadCommodityStates.input_to_load_brand), 
                              lambda callback: callback.data.startswith('load_engine_')),
                              F.data=='rewrite_boot_brand'))
    dp.callback_query.register(load_new_car.hybrid_handlers.input_model_to_load,
                              or_f(and_f(StateFilter(LoadCommodityStates.input_to_load_model), 
                              lambda callback: callback.data.startswith('load_brand_')),
                              F.data=='rewrite_boot_model'))
    dp.callback_query.register(load_new_car.hybrid_handlers.input_complectation_to_load,
                              or_f(and_f(StateFilter(LoadCommodityStates.input_to_load_complectation), 
                              lambda callback: callback.data.startswith('load_model_')),
                              F.data=='rewrite_boot_complectation'))

    dp.callback_query.register(load_new_car.second_hand_handlers.input_year_to_load,
                              or_f(and_f(StateFilter(LoadCommodityStates.input_to_load_year),
                              lambda callback: callback.data.startswith('load_complectation_')),
                              F.data=='rewrite_boot_year'))
    dp.callback_query.register(load_new_car.second_hand_handlers.input_mileage_to_load,
                              or_f(and_f(StateFilter(LoadCommodityStates.input_to_load_mileage),
                              lambda callback: callback.data.startswith('load_year_')),
                              F.data=='rewrite_boot_mileage'))
    dp.callback_query.register(load_new_car.second_hand_handlers.input_color_to_load,
                              or_f(and_f(StateFilter(LoadCommodityStates.input_to_load_color),
                              lambda callback: callback.data.startswith('load_mileage_')),
                              F.data=='rewrite_boot_color'))

    dp.callback_query.register(load_new_car.hybrid_handlers.input_price_to_load,
                              or_f(and_f(StateFilter(LoadCommodityStates.input_to_load_price),
                                  or_f(lambda callback: callback.data.startswith('load_complectation_'),
                                  lambda callback: callback.data.startswith('load_color_'))),
                              F.data=='rewrite_boot_price'))
    dp.message.register(load_new_car.hybrid_handlers.input_photo_to_load,
                              (and_f(StateFilter(LoadCommodityStates.input_to_load_photo), price_is_digit.PriceIsDigit())))
    dp.callback_query.register(load_new_car.hybrid_handlers.input_photo_to_load, 
                              F.data == 'rewrite_boot_photo')
    dp.message.register(load_new_car.get_output_configs.output_load_config_for_seller,
                              StateFilter(LoadCommodityStates.load_config_output), message_is_photo.MessageIsPhoto())


    @dp.callback_query()
    async def checker(callback: CallbackQuery, state: FSMContext):
      print('may')
      await callback.message.answer('Пролёт ' + callback.data)
      #await sell_part.commodity_requests.commodity_requests.commodity_reqests_by_seller(callback=callback)
      # await accept_registration_request_button.accept_registraiton(callback=callback)


    # dp.message.register(echo.bot_echo, StateFilter(default_state))

    dp.message.register(echo.bot_echo, StateFilter(default_state))


    dp.message.register(echo.bot_echo, StateFilter(default_state))
    '''bot_echo всегда в последней позиции'''

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


