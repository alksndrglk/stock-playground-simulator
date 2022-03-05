class RequestDoesNotMeetTheStandart(Exception):
    def __init__(self, message="Не понимаю сообщение."):
        self.message = message
        super().__init__(self.message)


class SymbolNotInPortfolio(Exception):
    def __init__(self, message="Такой акции в портфеле нет."):
        self.message = message
        super().__init__(self.message)


class OperationIsUnavailable(Exception):
    def __init__(self, message="Не достаточно средств. Операция недоступна."):
        self.message = message
        super().__init__(self.message)
