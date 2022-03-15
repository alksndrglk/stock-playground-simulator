from app.store.vk_api.dataclasses import Update, UpdateObject, Message


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
