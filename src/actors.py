"""One actor owns each conversation, its sockets, and its agent loop."""

import json
import logging
import os
from typing import Literal

from agents import Agent, RunConfig, Runner
from durable_actors import ActorSocket, AsyncActor, persisted
from durable_actors.json import JsonValue
from openai.types.responses import ResponseTextDeltaEvent
from pydantic import BaseModel

Event = dict[str, JsonValue]
logger = logging.getLogger(__name__)
agent = Agent[None](
    name="Chat",
    instructions="Be a concise, helpful assistant.",
    model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatHistory(AsyncActor[None, str, Event]):
    _messages: list[Message] = persisted(default_factory=list)
    _items_json: str = persisted("[]")

    async def load(self) -> list[Message]:
        return self._messages

    async def on_connect(self, socket: ActorSocket[None, Event]) -> None:
        socket.send(
            {
                "type": "history",
                "messages": [message.model_dump() for message in self._messages],
            }
        )

    async def on_message(self, socket: ActorSocket[None, Event], message: str) -> None:
        if not message.strip():
            return
        await self.broadcast({"type": "start", "prompt": message})
        try:
            items = json.loads(self._items_json)
            items.append({"role": "user", "content": message})
            result = Runner.run_streamed(
                agent, input=items, run_config=RunConfig(tracing_disabled=True)
            )
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(
                    event.data, ResponseTextDeltaEvent
                ):
                    await self.broadcast({"type": "delta", "text": event.data.delta})
            # Serialize before changing persisted fields so a failed run leaves history intact.
            items_json = json.dumps(result.to_input_list())
            reply = str(result.final_output)
        except Exception:  # noqa: BLE001 - one error boundary for the demo's model call
            logger.exception("Agent reply failed")
            await self.broadcast(
                {"type": "error", "message": "Reply failed. Check the actor server."}
            )
            return
        self._messages.extend(
            [
                Message(role="user", content=message),
                Message(role="assistant", content=reply),
            ]
        )
        self._items_json = items_json
        await self.broadcast({"type": "done"})
