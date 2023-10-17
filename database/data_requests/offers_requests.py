from database.tables.offers_history import ActiveOffers
from database.tables.start_tables import db


class OffersRequester:
    @staticmethod
    def store_data(data: dict):
        try:
            with db.atomic():
                ActiveOffers.create(**data)
                return True
        except Exception:
            return False

    @staticmethod
    def retrieve_data_by_buyer_id(buyer_id: int):
        try:
            with db.atomic():
                select_request = ActiveOffers.select().where(ActiveOffers.buyer == buyer_id).order_by(ActiveOffers.id.desc())
                return list(select_request)
        except Exception:
            return False