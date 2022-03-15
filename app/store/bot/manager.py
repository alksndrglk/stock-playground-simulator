import asyncio
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, NamedTuple, Tuple, Union
from logging import getLogger

from app.stock.models import (
    Game,
    Stock,
    StockMarketEvent,
    User,
)
from app.store.bot.const import (
    ALARM,
    ROUND_TIME,
    RULES_AND_GREET,
    add_to_chat_event,
    FINAL_SENTENCE,
    dollar,
    case,
    pushpin,
    chart,
    rong,
    check,
    minus,
    payload_answers,
)
from app.web.utils import periodic
from app.store.vk_api.dataclasses import Update, Message, UpdateObject
from app.store.bot.keyboards import STATIC, GREETING, END
from app.store.bot.conditions import VERB_TO_FUNCTION, RequestVerb
from app.store.bot.errors import (
    OperationIsUnavailable,
    RequestDoesNotMeetTheStandart,
    SymbolNotInPortfolio,
    SymbolNotInGame,
)

if TYPE_CHECKING:
    from app.web.app import Application


class ClientMessage(NamedTuple):
    verb: RequestVerb
    symbol: str
    quantity: int


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")
        self._auto_tasks = {}

    def parse_message(self, msg: str):
        try:
            command, symbol, quantity = msg.split()

            for verb in RequestVerb:
                if command.lower() == verb.value:
                    break
            else:
                self.logger("Unnown command in message")
                raise RequestDoesNotMeetTheStandart

            return ClientMessage(verb, symbol.upper(), int(quantity))
        except Exception:
            raise RequestDoesNotMeetTheStandart

    async def handle_updates(self, update: Update):
        text, keyboard = "", STATIC
        if update.object.action == add_to_chat_event:
            keyboard, text = GREETING, RULES_AND_GREET
        else:
            game: Union[Game, None] = await self.app.store.exchange.get_game(
                update.object.peer_id
            )
            payload = update.object.payload.get("command")
            if payload:
                asyncio.create_task(
                    self.app.store.vk_api.send_answer(
                        update.object.obj, text=payload_answers.get(payload)
                    )
                )
            if not game:
                if payload == "start":
                    keyboard, text = await self.start(update.object.peer_id)
                    self._auto_tasks[
                        update.object.peer_id
                    ] = asyncio.create_task(
                        self.round_automation(update.object.peer_id)
                    )
                elif payload == "show_state":
                    finished_game = await self.app.store.exchange.get_stats(
                        update.object.peer_id
                    )
                    keyboard, text = self.show_state(finished_game)
                else:
                    keyboard, text = GREETING, "НЕ ПОНИМАЮ"
            elif update.type == "message_event":
                if payload == "finished_bidding":
                    keyboard, text = await self.user_finished_bidding(
                        game, update.object
                    )
                if payload == "end":
                    keyboard, text = await self.finish_game(game)
                await self.app.store.exchange.update_game(game)
            elif update.type == "message_new":
                text = await self.message_processing(game, update.object)
        if text:
            await self.send_keyboard(
                update.object.peer_id,
                keyboard=keyboard,
                text=text,
            )

    @periodic(ROUND_TIME)
    async def round_automation(self, peer_id: int):
        game = await self.app.store.exchange.get_game(peer_id)
        if game.round_info["round_number"] <= 11:
            keyboard, text = await self.finish_round(game)
            await asyncio.gather(
                self.send_keyboard(
                    peer_id,
                    keyboard=keyboard,
                    text=text,
                ),
                self.app.store.exchange.update_game(game),
            )

    async def start(self, peer_id: int):
        players = await self.app.store.vk_api.get_conversation_members(peer_id)
        if not players:
            return GREETING, ALARM
        stocks = await self.app.store.exchange.create_game(players, peer_id)
        return STATIC, self.market_situtaion(stocks)

    async def send_keyboard(self, peer_id: int, keyboard=STATIC, text=" "):
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=peer_id,
                text=text,
                keyboard=keyboard,
            )
        )

    async def message_processing(self, game: Game, upd: UpdateObject):
        for_user = f"[id{upd.user_id}|{game.users[upd.user_id].user_name}]"
        if upd.user_id in game.round_info["finished_bidding"]:
            return f"{rong.decode()}{for_user}, Вы уже закончили торги."
        try:
            client_message = self.parse_message(upd.body)
            symbol = game.stocks.get(client_message.symbol)
            if not symbol:
                raise SymbolNotInGame
        except (RequestDoesNotMeetTheStandart, SymbolNotInGame) as e:
            return for_user + str(e)

        brokerage_account = game.users[upd.user_id].brokerage_account
        try:
            new_brokerage_acc = getattr(
                brokerage_account, VERB_TO_FUNCTION[client_message.verb]
            )(
                client_message.symbol,
                client_message.quantity,
                symbol.cost,
            )
            await self.app.store.exchange.update_brokerage_acc(
                new_brokerage_acc
            )
            return f"{check.decode()}{for_user},операция выполненa."
        except OperationIsUnavailable as e:
            return for_user + str(e)
        except SymbolNotInPortfolio as e:
            return for_user + str(e)

    async def user_finished_bidding(self, game: Game, upd: UpdateObject):
        for_user = f"[id{upd.user_id}|{game.users[upd.user_id].user_name}]"
        msg = f"{for_user} закончил торги.\n"
        if upd.user_id in game.round_info["finished_bidding"]:
            return (
                STATIC,
                f"{rong.decode()}{for_user}, Вы уже закончили торги.",
            )
        game.round_info["finished_bidding"].append(upd.user_id)
        if set([*game.users.keys()]) == set(
            game.round_info["finished_bidding"]
        ):
            return await self.finish_round(game)
        return STATIC, msg

    async def finish_round(self, game: Game):
        game.round_info["finished_bidding"] = []
        msg = f"📍{game.round_info['round_number']}й раунд торгов окончен\n"
        game.state[game.round_info["round_number"]] = {
            u: str(v) for u, v in game.users.items()
        }
        if game.round_info["round_number"] >= 11:
            return await self.finish_game(game)
        else:
            game.round_info["round_number"] += 1
            event = await self.market_events()
            new_stocks = await self.recalculate_stocks(game, event)
            msg += self.market_situtaion(new_stocks, event=event)
            msg += self.brokerage_accounts_info(
                [*game.users.values()], new_stocks
            )
            self._auto_tasks[game.chat_id].cancel()
            self._auto_tasks[game.chat_id] = asyncio.create_task(
                self.round_automation(game.chat_id)
            )
        return STATIC, msg

    async def finish_game(self, game: Game, msg=FINAL_SENTENCE):
        game.finished_at = datetime.now()
        msg += self.brokerage_accounts_info([*game.users.values()], game.stocks)
        if self._auto_tasks.get(game.chat_id):
            self._auto_tasks[game.chat_id].cancel()
            del self._auto_tasks[game.chat_id]
        return END, msg

    async def market_events(self) -> StockMarketEvent:
        return await self.app.store.exchange.get_event()

    async def recalculate_stocks(
        self, game: Game, event: StockMarketEvent
    ) -> Dict[str, Stock]:
        return await self.app.store.exchange.update_stocks(
            [*game.stocks.values()], event.diff
        )

    @staticmethod
    def show_state(game: Game):
        msg = "Полная статистика по раундам:\n"
        for r, s in game.state.items():
            msg += f"\n{pushpin.decode()}{r}й раунд\n"
            for u, b in s.items():
                msg += f"Пользователь [id{u}|] -- {b}\n"
        return END, msg

    @staticmethod
    def brokerage_accounts_info(
        users: List[User], stocks: Dict[str, Stock]
    ) -> str:
        msg = f"\nСостояние инвестиционных портфелей{case.decode()} :\n\n"
        dash = {}
        for u in users:
            fc = 0
            for k, v in u.brokerage_account.portfolio.items():
                fc += v * stocks[k].cost
            u_msg = f".[id{u.user_id}|{u.user_name}]\n{str(u)}\nCтоимость портфеля: {fc:.2f}{dollar.decode()}"
            total = fc + u.brokerage_account.points
            u_msg += (
                f"\n{minus.decode()*5}\nИтого:{total:.2f}{dollar.decode()}\n\n"
            )
            dash[u.user_id] = [total, u_msg]
        for i, k in enumerate(
            sorted(dash.items(), key=lambda e: e[1][0], reverse=True), 1
        ):
            if i == 1:
                k[1][1] = k[1][1][:-2] + f"{'❗'*3}Лидер{'❗'*3}\n\n"
            msg += str(i) + k[1][1]
        return msg

    @staticmethod
    def market_situtaion(
        stocks: Dict[str, Stock],
        event: StockMarketEvent = None,
        text: str = f"{chart.decode()} Цены на акции:\n",
    ) -> str:
        if event:
            text = str(event) + text
        text += "\n".join(str(s) for s in stocks.values())
        return text
