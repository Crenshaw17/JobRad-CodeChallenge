from enum import Enum
import datetime as dt
from pydantic import BaseModel


# a helper enum for BaseMessage sendertypes
class SenderType(Enum):
    NOTDEFINED = 0
    CLIENT = 1
    CUSTOMER_SERVICE = 2


# a data format class for transmittable messages between client and server
class BaseMessage(BaseModel):
    chat_id: str
    msg: str
    sender_type: int
    sender_name: str
    timestamp: float
    is_seen: bool


# a helper function to create a BaseMessage object
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
