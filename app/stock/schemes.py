from marshmallow import Schema, fields
from marshmallow.validate import Range

class StockSchema(Schema):
    id = fields.Int(required=False)
    symbol = fields.Str(required=True)
    description = fields.Str(required=True)
    cost = fields.Float(required=True)


class EventSchema(Schema):
    id = fields.Int(required=False)
    message = fields.Str(required=True)
    diff = fields.Float(required=True,validate=Range(min=0, max=10)


class StockListSchema(Schema):
    stocks = fields.Nested(StockSchema, many=True)


class EventListSchema(Schema):
    events = fields.Nested(EventSchema, many=True)


class ChatIdSchema(Schema):
    chat_id = fields.Int()
