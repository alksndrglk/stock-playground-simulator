from aiohttp_apispec import request_schema, response_schema, querystring_schema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class StockAddView(AuthRequiredMixin, View):
    pass


class StockListView(AuthRequiredMixin, View):
    pass


class EventAddView(AuthRequiredMixin, View):
    pass


class EventListView(AuthRequiredMixin, View):
    pass


class GameStatisticView(AuthRequiredMixin, View):
    pass
