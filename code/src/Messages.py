from enum import Enum
import datetime as dt
from pydantic import BaseModel


# a helper enum for BaseMessage sendertypes
class SenderType(Enum):
    NOTDEFINED = 0
    CLIENT = 1
    CUSTOMER_SERVICE = 2


# a class for transmitting messages between client and server
class BaseMessage(BaseModel):
    chat_id: str
    msg: str
    sender_type: int
    sender_name: str
    timestamp: float
    is_seen: bool


def compose_msg(m: str, chat_id: str, sender_type: SenderType, sender_name: str):
    m = BaseMessage(
        chat_id=chat_id,
        msg=m,
        sender_type=int(sender_type.value),
        sender_name=sender_name,
        timestamp=dt.datetime.timestamp(dt.datetime.now()),
        is_seen=False
    )
    return m


# convert incoming json chat data to BaseMessage type
def chat_json_to_basemessages(chat_response_json):
    base_msgs = []
    for m in chat_response_json:
        base_msgs.append(BaseMessage(**m))
    return base_msgs


class MsgOrigin(Enum):
    ClientMsg = 1
    CompanyMsg = 2


class MsgType(Enum):
    TextMsg = 1
    AudioMsg = 2
    VideoMsg = 3
    PhotoMsg = 4


# class providing basic message functionality for all child classes
class BaseMessageOld():
    msg_origin = None
    msg_type = None
    sent_date = None
    seen_date = None
    sent_from = None
    content = None

    def __init__(self, msg_type: MsgType):
        self.msg_type = MsgType

    def set_seen(self, timestamp:dt = None):
        if timestamp is not None:
            self.seen_date = timestamp
        else:
            self.seen_date = dt.datetime.now()


class ClientMessage(BaseMessageOld):
    def __init__(self, msg_origin: MsgOrigin):
        self.msg_origin = MsgOrigin.ClientMsg


class TextMsg(BaseMessageOld):
    def __init__(self, content=""):
        super().__init__(MsgType.TextMsg)
        self.content = content
        self.sent_date = dt.datetime.now()


class Chat():
    msg_history = []

    def chat_from_db(self, msgs: list):
        for msg in msgs:
            self.msg_history.append(msg)
