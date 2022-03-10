from app.web.app import app

ROUND_TIME = 60
FINAL_SENTENCE = "Финальные результаты торгов на бирже:\n"
RULES_AND_GREET = """
   Для корректной работы бота, дайте ему права Администратора в настройках.\n
   Управление осуществляется в сообщениях командами /sell и /buy.\n
   Приемер команды: /sell AAPL 100.\n
   Когда все игроки будут готовы нажмите на кнопку СТАРТ внизу.\n
   """

add_to_chat_event = {
    "type": "chat_invite_user",
    "member_id": -app.config.bot.group_id,
}
