from enum import Enum


class RequestVerb(Enum):
    SELL = "/sell"
    BUY = "/buy"


VERB_TO_FUNCTION = {RequestVerb.SELL: "sell", RequestVerb.BUY: "buy"}
