from unittest.mock import AsyncMock

import pytest
from app.store.bot.dataclassess import VkUser
from app.store.vk_api.dataclasses import Update, UpdateObject, Message
from app.store.bot.keyboards import END, GREETING, STATIC
from tests.data import OBJ_BUY_MSG, OBJ_FINISHED_BIDDING, STOCKS


class TestFinishRound:
    async def test_success(self, store, game_2_usrs):
        upd = OBJ_FINISHED_BIDDING[0].object
        k, m = await store.bots_manager.finish_round(game_2_usrs)
        assert k == STATIC
        assert "раунд торгов окончен" in m


class TestUserFinishedBidding:
    async def test_success(self, store, game_2_usrs):
        upd = OBJ_FINISHED_BIDDING[0].object

        k, m = await store.bots_manager.user_finished_bidding(game_2_usrs, upd)
        assert k == STATIC
        assert "закончил торги" in m

    async def test_already(self, store, game_2_usrs):
        upd = OBJ_FINISHED_BIDDING[0].object
        game_2_usrs.round_info["finished_bidding"] = [upd.user_id]

        k, m = await store.bots_manager.user_finished_bidding(game_2_usrs, upd)
        assert k == STATIC
        assert "Вы уже закончили торги." in m

    async def test_all_finished(self, store, game):
        upd = OBJ_FINISHED_BIDDING[0].object

        store.bots_manager.finish_round = AsyncMock(
            return_value=(STATIC, "раунд торгов окончен")
        )
        k, m = await store.bots_manager.user_finished_bidding(game, upd)
        assert k == STATIC
        assert "раунд торгов окончен" in m


class TestStartGame:
    async def test_success(self, store):
        store.vk_api.get_conversation_members = AsyncMock(
            return_value=[
                VkUser(vk_id=3, user_name="Olef"),
                VkUser(vk_id=4, user_name="Leila"),
            ]
        )
        store.exchange.create_game = AsyncMock(return_value=STOCKS)
        k, m = await store.bots_manager.start(1)
        assert len(store.bots_manager._auto_tasks) == 1
        assert k == STATIC
        assert m == store.bots_manager.market_situtaion(STOCKS)

    async def test_no_players(self, store):
        from app.store.bot.const import ALARM

        store.vk_api.get_conversation_members = AsyncMock(return_value=[])
        k, m = await store.bots_manager.start(1)
        assert k == GREETING
        assert m == ALARM


class TestMessageProcessing:
    async def test_operation_done(self, store, game):
        upd = OBJ_BUY_MSG[0].object
        store.exchange.update_brokerage_acc = AsyncMock(
            return_value=game.users[upd.user_id].brokerage_account
        )
        msg = await store.bots_manager.message_processing(game, upd)
        assert "операция выполненa" in msg

    @pytest.mark.parametrize(
        "msg, answ",
        [
            ("sel aapl 10", ". Не понимаю сообщение."),
            ("sell aap 10", ". Такая акция не играется на бирже."),
            ("sell amzn 10", ". Такой акции в портфеле нет."),
            ("buy aapl 100", ". Недостаточно средств. Операция недоступна."),
        ],
    )
    async def test_parse_message_error(self, store, game, msg, answ):
        upd = OBJ_BUY_MSG[0].object
        upd.body = msg
        store.exchange.update_brokerage_acc = AsyncMock(
            return_value=game.users[upd.user_id].brokerage_account
        )
        msg = await store.bots_manager.message_processing(game, upd)
        assert msg.endswith(answ)


class TestHandleUpdates:
    async def test_new_message(self, store):
        await store.bots_manager.handle_updates(
            Update(
                type="message_new",
                object=UpdateObject(
                    id=1,
                    peer_id=1,
                    user_id=2121,
                    body="",
                    action={},
                    payload={},
                    obj={},
                ),
            )
        )
        assert store.vk_api.send_message.call_count == 1
        message: Message = store.vk_api.send_message.mock_calls[0].args[0]
        assert message.peer_id == 1
        assert message.text
        assert message.keyboard
        store.vk_api.send_message.reset_mock()

    async def test_start_button(self, store):
        store.bots_manager.start = AsyncMock(return_value=(STATIC, "Stocks..."))
        await store.bots_manager.handle_updates(
            Update(
                type="message_event",
                object=UpdateObject(
                    id=1,
                    peer_id=1,
                    user_id=2121,
                    body="",
                    action={},
                    payload={"command": "start"},
                    obj={},
                ),
            )
        )
        assert store.vk_api.send_answer.call_count == 1
        message: Message = store.vk_api.send_message.mock_calls[0].args[0]
        assert message.peer_id == 1
        assert message.text == "Stocks..."
        assert message.keyboard == STATIC
        store.vk_api.send_message.reset_mock()
        store.vk_api.send_answer.reset_mock()

    async def test_add_to_chat(self, store):
        from app.store.bot.const import RULES_AND_GREET, add_to_chat_event

        await store.bots_manager.handle_updates(
            Update(
                type="message_event",
                object=UpdateObject(
                    id=1,
                    peer_id=1,
                    user_id=2121,
                    body="",
                    action=add_to_chat_event,
                    payload={},
                    obj={},
                ),
            )
        )
        assert store.vk_api.send_message.call_count == 1
        message: Message = store.vk_api.send_message.mock_calls[0].args[0]
        assert message.peer_id == 1
        assert message.keyboard == GREETING
        assert message.text == RULES_AND_GREET
        store.vk_api.send_message.reset_mock()

    async def test_show_state(self, store, finished_game):
        store.exchange.get_stats = AsyncMock(return_value=finished_game)
        await store.bots_manager.handle_updates(
            Update(
                type="message_event",
                object=UpdateObject(
                    id=1,
                    peer_id=1,
                    user_id=2121,
                    body="",
                    action={},
                    payload={"command": "show_state"},
                    obj={},
                ),
            )
        )
        assert store.vk_api.send_answer.call_count == 1
        assert store.vk_api.send_message.call_count == 1
        message: Message = store.vk_api.send_message.mock_calls[0].args[0]
        assert message.peer_id == 1
        assert message.text.startswith("Полная статистика по раундам")
        assert message.keyboard == END
        store.vk_api.send_message.reset_mock()
        store.vk_api.send_answer.reset_mock()

    async def test_end_game(self, store, game):
        from app.store.bot.const import FINAL_SENTENCE

        store.exchange.get_game = AsyncMock(return_value=game)
        await store.bots_manager.handle_updates(
            Update(
                type="message_event",
                object=UpdateObject(
                    id=1,
                    peer_id=1,
                    user_id=2121,
                    body="",
                    action={},
                    payload={"command": "end"},
                    obj={},
                ),
            )
        )
        assert store.vk_api.send_answer.call_count == 1
        assert store.vk_api.send_message.call_count == 1
        message: Message = store.vk_api.send_message.mock_calls[0].args[0]
        assert message.peer_id == 1
        assert message.text.startswith(FINAL_SENTENCE)
        assert message.keyboard == END
        store.vk_api.send_message.reset_mock()
        store.vk_api.send_answer.reset_mock()
