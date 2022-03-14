import json


GREETING = {
    "one_time": True,
    "buttons": [
        [
            {
                "action": {
                    "type": "callback",
                    "payload": '{"command": "start"}',
                    "label": "Старт",
                },
                "color": "positive",
            },
        ]
    ],
}


STATIC = {
    "one_time": True,
    "buttons": [
        [
            {
                "action": {
                    "type": "callback",
                    "payload": '{"command": "finished_bidding"}',
                    "label": "Закончить торги",
                },
                "color": "primary",
            },
            {
                "action": {
                    "type": "callback",
                    "payload": '{"command": "end"}',
                    "label": "СТОП",
                },
                "color": "negative",
            },
        ]
    ],
}


END = {
    "one_time": True,
    "buttons": [
        [
            {
                "action": {
                    "type": "callback",
                    "payload": '{"command": "show_state"}',
                    "label": "Показать подробные результаты",
                },
                "color": "primary",
            },
            {
                "action": {
                    "type": "callback",
                    "payload": '{"command": "start"}',
                    "label": "Играть Заново",
                },
                "color": "positive",
            },
        ]
    ],
}
