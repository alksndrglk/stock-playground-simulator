from dataclasses import dataclass, field


@dataclass
class UpdateObject:
    id: int
    peer_id: int
    body: str
    action: str


@dataclass
class Update:
    type: str
    object: UpdateObject


@dataclass
class Message:
    peer_id: int
    text: str
    keyboard : dict = field(default_factory=dict)
