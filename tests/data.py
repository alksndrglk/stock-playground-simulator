from app.store.vk_api.dataclasses import Update, UpdateObject


START_BUTTON = {
    "ts": "2620",
    "updates": [
        {
            "type": "message_event",
            "object": {
                "user_id": 11142115,
                "peer_id": 2000000006,
                "event_id": "5a012c46a3b6",
                "payload": {"command": "start"},
            },
            "group_id": 210570816,
            "event_id": "7061865429a920647de6adeaec8205c095c717a0",
        }
    ],
}

OBJ_START_BUTTON = [
    Update(
        type="message_event",
        object=UpdateObject(
            id=None,
            peer_id=2000000006,
            user_id=11142115,
            body=None,
            action={},
            payload={"command": "start"},
            obj={
                "user_id": 11142115,
                "peer_id": 2000000006,
                "event_id": "5a012c46a3b6",
                "payload": {"command": "start"},
            },
        ),
    )
]

BUY_MSG = {
    "ts": "2621",
    "updates": [
        {
            "type": "message_new",
            "object": {
                "message": {
                    "date": 1647413987,
                    "from_id": 11142115,
                    "id": 0,
                    "out": 0,
                    "attachments": [],
                    "conversation_message_id": 475,
                    "fwd_messages": [],
                    "important": False,
                    "is_hidden": False,
                    "peer_id": 2000000006,
                    "random_id": 0,
                    "text": "buy aapl 10",
                },
                "client_info": {
                    "button_actions": [
                        "text",
                        "vkpay",
                        "open_app",
                        "location",
                        "open_link",
                        "callback",
                        "intent_subscribe",
                        "intent_unsubscribe",
                    ],
                    "keyboard": True,
                    "inline_keyboard": True,
                    "carousel": True,
                    "lang_id": 0,
                },
            },
            "group_id": 210570816,
            "event_id": "bfaae0433516b6812a71e7fd7a20be6619c7d54b",
        }
    ],
}

OBJ_BUY_MSG = [
    Update(
        type="message_new",
        object=UpdateObject(
            id=0,
            peer_id=2000000006,
            user_id=11142115,
            body="buy aapl 10",
            action={},
            payload={},
            obj={},
        ),
    )
]

SELL_MSG = {
    "ts": "2622",
    "updates": [
        {
            "type": "message_new",
            "object": {
                "message": {
                    "date": 1647413992,
                    "from_id": 11142115,
                    "id": 0,
                    "out": 0,
                    "attachments": [],
                    "conversation_message_id": 477,
                    "fwd_messages": [],
                    "important": False,
                    "is_hidden": False,
                    "peer_id": 2000000007,
                    "random_id": 0,
                    "text": "sell aapl 5",
                },
                "client_info": {
                    "button_actions": [
                        "text",
                        "vkpay",
                        "open_app",
                        "location",
                        "open_link",
                        "callback",
                        "intent_subscribe",
                        "intent_unsubscribe",
                    ],
                    "keyboard": True,
                    "inline_keyboard": True,
                    "carousel": True,
                    "lang_id": 0,
                },
            },
            "group_id": 210570816,
            "event_id": "6ad6cf776aa8784bf04e287f02970ab7da9cfad5",
        }
    ],
}

OBJ_SELL_MSG = [
    Update(
        type="message_new",
        object=UpdateObject(
            id=0,
            peer_id=2000000006,
            user_id=11142115,
            body="sell aapl 5",
            action={},
            payload={},
            obj={},
        ),
    )
]

FINISHED_BIDDING = {
    "ts": "2623",
    "updates": [
        {
            "type": "message_event",
            "object": {
                "user_id": 11142115,
                "peer_id": 2000000006,
                "event_id": "18ddd295307f",
                "payload": {"command": "finished_bidding"},
            },
            "group_id": 210570816,
            "event_id": "3135041b73d850c03bc7a0b1072f9c7932316b2d",
        }
    ],
}

OBJ_FINISHED_BIDDING = [
    Update(
        type="message_event",
        object=UpdateObject(
            id=None,
            peer_id=2000000006,
            user_id=11142115,
            body=None,
            action={},
            payload={"command": "finished_bidding"},
            obj={
                "user_id": 11142115,
                "peer_id": 2000000006,
                "event_id": "18ddd295307f",
                "payload": {"command": "finished_bidding"},
            },
        ),
    )
]

END = {
    "ts": "2624",
    "updates": [
        {
            "type": "message_event",
            "object": {
                "user_id": 11142115,
                "peer_id": 2000000006,
                "event_id": "ccc17ef6319a",
                "payload": {"command": "end"},
            },
            "group_id": 210570816,
            "event_id": "714229c1b339ecc525b1aa3057898cf4b761b350",
        }
    ],
}

OBJ_END = [
    Update(
        type="message_event",
        object=UpdateObject(
            id=None,
            peer_id=2000000006,
            user_id=11142115,
            body=None,
            action={},
            payload={"command": "end"},
            obj={
                "user_id": 11142115,
                "peer_id": 2000000006,
                "event_id": "ccc17ef6319a",
                "payload": {"command": "end"},
            },
        ),
    )
]
