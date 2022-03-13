from app.web.app import app

ROUND_TIME = 60
FINAL_SENTENCE = "Финальные результаты торгов на бирже:\n"
RULES_AND_GREET = """
   Для корректной работы бота, дайте ему права Администратора в настройках.❗\n
   Управление осуществляется в сообщениях командами sell и buy.\n
   Пример команд: sell AAPL 100, buy amzn 54\n
   Один раунд торгов длится не более 1мин\n 
   Когда все игроки будут готовы нажмите на кнопку СТАРТ внизу.\n
   """

add_to_chat_event = {
    "type": "chat_invite_user",
    "member_id": -app.config.bot.group_id,
}

dollar = b"\xF0\x9F\x92\xB2"
case = b"\xf0\x9f\x92\xbc"
chart = b"\xF0\x9F\x93\x88"
pushpin = b"\xF0\x9F\x93\x8D"
