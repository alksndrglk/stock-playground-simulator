from app.web.app import app

ROUND_TIME = 60
FINAL_SENTENCE = "\nФинальные результаты торгов на бирже"
ALARM = "Для корректной работы бота, дайте ему права Администратора в настройках.❗\n"
RULES_AND_GREET = (
    ALARM
    + """
   Управление осуществляется в сообщениях командами sell и buy.\n
   Пример команд: sell AAPL 100, buy amzn 54\n
   Один раунд торгов длится не более 1мин\n 
   Когда все игроки будут готовы нажмите на кнопку СТАРТ внизу.\n
   """
)

add_to_chat_event = {
    "type": "chat_invite_user",
    "member_id": -app.config.bot.group_id,
}

payload_answers = {
    "start": "Поехали!",
    "end": "Заканчиваем игру.",
    "show_state": "Выгружаем статистику.",
    "finished_bidding": "Игрок закончил торги.",
}

dollar = b"\xF0\x9F\x92\xB2"
case = b"\xf0\x9f\x92\xbc"
chart = b"\xF0\x9F\x93\x88"
pushpin = b"\xF0\x9F\x93\x8D"
rong = b"\xF0\x9F\x94\x95"
check = b"\xE2\x9C\x94"
minus = b"\xE2\x9E\x96"
