from __future__ import annotations
from typing import TYPE_CHECKING, TypeAlias
from typing import Annotated, Literal, Optional, Union
from pydantic import Field
from durable_actors.generated import ClientModel
from typing_extensions import TypeAliasType

class Message(ClientModel):
    role: Annotated[Literal['user', 'assistant'], Field(title='Role')]
    content: Annotated[str, Field(title='Content')]
RpcMethodLoadResult: TypeAlias = list[Message]
if TYPE_CHECKING:
    JsonValue: TypeAlias = Optional[Union[str, int, float, bool, list['JsonValue'], dict[str, 'JsonValue']]]
else:
    JsonValue = TypeAliasType('JsonValue', Optional[Union[str, int, float, bool, list['JsonValue'], dict[str, 'JsonValue']]])
if TYPE_CHECKING:
    SocketMetadata: TypeAlias = None
else:
    SocketMetadata = TypeAliasType('SocketMetadata', None)
SocketIncoming: TypeAlias = str
SocketOutgoing: TypeAlias = dict[str, JsonValue]
Tag: TypeAlias = str

class SocketState(ClientModel):
    """
    Public persisted fields of the actor.
    """

class SocketEmittedState(ClientModel):
    """
    Complete current values of the actor's emitted fields.
    """

class SocketStatePatch(ClientModel):
    """
    Changed emitted fields; omitted fields are unchanged.
    """

class ContractTypes(ClientModel):
    """
    Named wire types used by this generated actor client.
    """
    RpcMethod_load_Result: RpcMethodLoadResult
    SocketMetadata_1: Annotated[SocketMetadata | None, Field(alias='SocketMetadata')]
    SocketIncoming_1: Annotated[SocketIncoming, Field(alias='SocketIncoming')]
    SocketOutgoing_1: Annotated[SocketOutgoing, Field(alias='SocketOutgoing')]
    SocketState_1: Annotated[SocketState, Field(alias='SocketState')]
    SocketEmittedState_1: Annotated[SocketEmittedState, Field(alias='SocketEmittedState')]
    SocketStatePatch_1: Annotated[SocketStatePatch, Field(alias='SocketStatePatch')]
