from aiogram.types import CallbackQuery
from handlers.state_handlers.choose_car_for_buy.hybrid_handlers import CommodityRequester
from handlers.callback_handlers.callback_handler_start_buy import PersonRequester
from database.data_requests.offers_requests import OffersRequester


async def confirm_from_seller(callback: CallbackQuery):
    callback_encoding = callback.data.split(':')
    cars_id_range = callback_encoding[1]
    cars_id_range = cars_id_range.split(' ')

    seller_id = callback.from_user.id
    cars_id_range = tuple(map(int, cars_id_range))
    buyer_id = int(callback_encoding[3])

    need_car = CommodityRequester.get_car_for_offer(seller_id=seller_id, car_range_id=cars_id_range)
    buyer_person = PersonRequester.get_user_for_id(user_id=buyer_id, user=True)
    seller_person = PersonRequester.get_user_for_id(user_id=seller_id, seller=True)
    print(buyer_person)
    print(seller_id)
    buyer_person = buyer_person[0]
    seller_person = seller_person[0]
    need_car = need_car[0]

    data_from_load_on_history_offers = {'seller': seller_person,
                                        'buyer': buyer_person,
                                        'car': need_car}

    OffersRequester.store_data(data_from_load_on_history_offers)

    message_id = callback.message.message_id
    await callback.message.chat.delete_message(callback.message.chat.id, message_id=message_id)


    #'confirm_from_seller:' + cars_id_range + ':to_buyer' + buyer_id)