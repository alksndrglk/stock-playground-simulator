from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class UpdateObject:
    id: int
    peer_id: int
    body: str
    action: str
    payload : dict = field(default_factory=dict)


@dataclass
class Update:
    type: str
    object: UpdateObject


@dataclass
class Message:
    peer_id: int
    text: str
    keyboard : dict['str', Union[bool,list]] = field(default_factory=dict)
