"""Typed async actor handles sharing the synchronous namespace models."""
from __future__ import annotations
import builtins as _builtins
from typing import TypeAlias as _TypeAlias, Literal as _Literal
from durable_actors.async_client import AsyncActorTransport as _ActorTransport
from durable_actors.generated import Unset as _Unset
from durable_actors.proxy import prepare_async_authorization as _prepare_authorization
from durable_actors.client import SocketGrant as _SocketGrant
from pydantic import TypeAdapter as _TypeAdapter
from . import actors as _sync_actors
from . import _chathistory as _client_0
from . import _chathistory_models as _models_0

class ChatHistory:
    """Clients and types for ChatHistory actors."""
    Stub: _TypeAlias = _client_0.AsyncStub
    Metadata: _TypeAlias = _models_0.SocketMetadata | None
    Incoming: _TypeAlias = _models_0.SocketIncoming
    Outgoing: _TypeAlias = _models_0.SocketOutgoing
    State: _TypeAlias = _models_0.SocketState
    EmittedState: _TypeAlias = _models_0.SocketEmittedState
    StatePatch: _TypeAlias = _models_0.SocketStatePatch
    Message: _TypeAlias = _models_0.Message

    @_builtins.staticmethod
    def get(actor_id: _builtins.str, transport: _ActorTransport | None = None) -> _client_0.AsyncStub:
        """Return a async actor handle without sending a request.
        
        Args:
            actor_id: Identity of the actor to call.
            transport: Optional caller-owned transport. Uses the SDK-managed
                transport when omitted.
        
        The returned Stub provides the actor's typed RPC methods.
        """
        return _client_0.AsyncStub(actor_id, transport)

    Authorization: _TypeAlias = _sync_actors.ChatHistory.Authorization

    @_builtins.staticmethod
    async def prepare_websocket(authorization: ChatHistory.Authorization, transport: _ActorTransport | None = None) -> _SocketGrant:
        """Issue browser access after authenticating the user and authorizing this actor."""
        return await _prepare_authorization(_TypeAdapter(ChatHistory.Authorization).validate_python(authorization), transport)

    class Methods:
        """Argument tuples and return types for each actor RPC."""
        class load:
            """Types for ChatHistory.load."""
            Args: _TypeAlias = _builtins.tuple[()]
            Result: _TypeAlias = _models_0.RpcMethodLoadResult

__all__ = ['ChatHistory']
