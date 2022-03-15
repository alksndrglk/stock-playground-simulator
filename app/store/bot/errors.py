class RequestDoesNotMeetTheStandart(Exception):
    def __init__(self, message=". Не понимаю сообщение."):
        self.message = message
        super().__init__(self.message)


class SymbolNotInPortfolio(Exception):
    def __init__(self, message=". Такой акции в портфеле нет."):
        self.message = message
        super().__init__(self.message)


class SymbolNotInGame(Exception):
    def __init__(self, message=". Такая акция не играется на бирже."):
        self.message = message
        super().__init__(self.message)


class OperationIsUnavailable(Exception):
    def __init__(self, message=". Недостаточно средств. Операция недоступна."):
        self.message = message
        super().__init__(self.message)
