from aiogram.types import CallbackQuery

from handlers.callback_handlers.confirm_from_seller_callback_handler import OffersRequester

from handlers.pagination_message_editor import paginaton_message_editor
'''#Пишем блок истории запросов#'''


async def format_history_data(offers_for_user: list) -> list:
    result_stack = list()

    for offer in offers_for_user:
        formatted_price = '{:,}'.format(offer.car.price).replace(',', '.')
        print(formatted_price)
        dealship_name = offer.seller.dealship_name
        if dealship_name:
            result_text = f'''
          🚘 Салон: {dealship_name}\n💰 Стоимость: {formatted_price}\nКонтакты салона:\n  - {offer.seller.phone_number}\n  - {offer.seller.dealship_address}
                        '''
        else:
            seller_full_name = offer.seller.surname + ' ' + offer.seller.name + ' ' + offer.seller.patronymic
            result_text = f'''
            👨🏻 Частное лицо: {seller_full_name}\n💰 Стоимость: {formatted_price}\nКонтакты:\n - {offer.seller.phone_number}
            '''
        result_stack.append(result_text)

    return result_stack

async def offers_to_user_history_handler(callback: CallbackQuery):
    non_history = False

    offers = OffersRequester.retrieve_data_by_buyer_id(buyer_id=callback.from_user.id)
    if offers:
        formatted_offers_history = await format_history_data(offers)
    else:
        non_history = True

    if not non_history:
        await paginaton_message_editor(lexicon_code='buttons_offers_history_for_buyer_output',
                                       message_stack=formatted_offers_history,
                                       delete_mode=True)
    else:
        await travel_editor.edit_message(lexicon_key='non_history_data')
