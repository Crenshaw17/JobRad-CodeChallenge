from http.client import HTTPException
from Messages import BaseMessage, SenderType
from fastapi import FastAPI, APIRouter
import uvicorn
from tinydb import TinyDB
from tinydb import Query
import json
import os
import secrets
import datetime
import uuid


# create the server
app = FastAPI(title="ChatAppServer", description="a simple chat server for receiving messages from client")


# in-memory database class for access handling
class ChatAppDB:
    db = None

    def __init__(self, db_path: str):
        self.db = TinyDB(db_path)

    # delete all db contents
    def clear_db(self):
        self.db.truncate()

    def add_new_chat(self, c_id: str):
        chatquery = Query()
        chat = self.db.search(chatquery["cid"] == c_id)
        if len(chat) > 0:
            print("c_id already exists!")
        else:
            self.db.insert({"cid": c_id, "msgs": []})
        return c_id

    def add_msg_to_chat(self, c_id: str, msg: {}):
        chatquery = Query()
        msgs = self.db.search(chatquery["cid"] == c_id)
        if len(msgs) < 1:
            raise HTTPException("invalid cid while trying to add msg to db")
        msgs = msgs[0]["msgs"]
        msgs.append(msg)
        self.db.update({"msgs": msgs}, chatquery["cid"] == c_id)

    # retrieve all msgs from a chat
    def get_all_msgs(self, c_id: str, unread=False):
        chatquery = Query()
        try:
            msgs = self.db.search(chatquery["cid"] == c_id)[0]["msgs"]
            # filter for unread messages if necessary
            if unread:
                unread_msgs = []
                for m in msgs:
                    if m["is_seen"] == False:
                        unread_msgs.append(m)
                msgs = unread_msgs
            return msgs
        except:
            # invalic cid
            return []

    # get the ids for all nonempty chats in the db
    def get_all_chat_ids(self):
        chat_ids = []
        for chat in self.db:
            if len(chat["msgs"]) > 0:
                chat_ids.append(chat["cid"])
        return chat_ids


# main chat backend class which handles requests received by the server object
class ChatAppServer():
    db_path = None
    db = None

    def __init__(self, db_path=None):
        self.db_path = db_path
        self.init_db()
        self.api_router = APIRouter()
        self.api_router.add_api_route("/hello", self.test, methods=["GET"])
        self.api_router.add_api_route("/chats/newchat", self.new_chat, methods=["GET"])
        self.api_router.add_api_route("/chats/{chat_id}", self.read_chat, methods=["GET"])
        self.api_router.add_api_route("/chats", self.read_chats, methods=["GET"])
        self.api_router.add_api_route("/chats/{chat_id}", self.receive_msg, methods=["PUT"])

    # load db
    def init_db(self):
        db = None
        if not os.path.isfile(self.db_path):
            print(">> no db found | creating")
        else:
            print(">> there is a db!")
        self.db = ChatAppDB(self.db_path)

    # create a short random chat_id
    @staticmethod
    def create_chat_id():
        return secrets.token_hex(6)

    # add a new message to the db
    def add_new_msg(self, msg: BaseMessage):
        self.db.add_msg_to_chat(msg.chat_id, self.compose_db_msg(msg))

    # create a db message using BaseMessage object or string
    @staticmethod
    def compose_db_msg(base_msg):
        m = {}
        if isinstance(base_msg, BaseMessage):
            m = {
                "m_id": uuid.uuid4().hex,
                "text": str(base_msg.msg),
                "timestamp": datetime.datetime.timestamp(datetime.datetime.now()),
                "cid": base_msg.chat_id,
                "is_seen": False,
                "sender_name": base_msg.sender_name,
                "sender_type": base_msg.sender_type
            }
        else:
            m = {
                "m_id": uuid.uuid4().hex,
                "text": str(base_msg),
                "timestamp": datetime.datetime.timestamp(datetime.datetime.now()),
                "cid": "",
                "is_seen": False,
                "sender_name": "garfield",
                "sender_type": SenderType.CLIENT.value
            }
        return m

    # get all messages for a chat from db as list of BaseMessage
    # RETURNS: list[BaseMessage]
    def get_msgs(self, c_id: str, unread=False):
        msgs = self.db.get_all_msgs(c_id, unread=unread)
        base_msgs = []
        for m in msgs:
            base_msgs.append(self.msg_to_basemessage(m))
        return base_msgs

    # get all available chats
    # RETURNS: list[{str : list[BaseMessage]}]
    def get_chats(self, unread=False):
        chat_ids = self.db.get_all_chat_ids()
        chats = []
        for c_id in chat_ids:
            msgs = self.get_msgs(c_id, unread)
            if len(msgs) > 0:
                chats.append({c_id : msgs})
        return chats

    # convert db message to BaseMessage type
    @staticmethod
    def msg_to_basemessage(m: {}):
        base_msg = BaseMessage(
            chat_id=m["cid"],
            msg=m["text"],
            sender_type=m["sender_type"],
            sender_name=m["sender_name"],
            timestamp=m["timestamp"],
            is_seen=m["is_seen"]
        )
        return base_msg

    # calls the db and adds a new chat entry using a generated chat_id
    def create_new_chat(self):
        chat_id = self.create_chat_id()
        self.db.add_new_chat(chat_id)
        print("chat id:", chat_id)
        return chat_id

    ### functions for REST server interaction

    ### API call for getting all chat messages for specific c_id
    def read_chat(self, chat_id: str, unread: bool = False):
        base_msgs = self.get_msgs(chat_id, unread=unread)
        return base_msgs

    ### API call for getting all chats in the db
    def read_chats(self, unread: bool = False):
        all_chats = self.get_chats(unread)
        return all_chats

    ### test API call
    @staticmethod
    def test():
        return "world"

    ### API call for creating new chat
    def new_chat(self):
        chad_id = self.create_new_chat()
        return chad_id

    ### API call for adding a new message to chat database
    def receive_msg(self, chat_id: str, msg: BaseMessage):
        self.add_new_msg(msg)


def main():

    path = os.path.join(os.path.abspath(os.getcwd()), "config.json")
    with open(path, 'r') as f:
        configfile = json.load(f)
    db_path = configfile["db_path"]
    print("db path: ", db_path)

    # create server
    server = ChatAppServer(db_path)
    app.include_router(server.api_router)

    # run server | needs to map ports on host | accessible via localhost:8080
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")


def initial_test(server: ChatAppServer):
    print("db content: ", server.db.db.all())
    c_id1 = server.db.add_new_chat(server.create_chat_id())
    print("db content: ", server.db.db.all())
    c_id2 = server.db.add_new_chat(server.create_chat_id())
    print("db content: ", server.db.db.all())
    server.db.add_msg_to_chat(c_id1, server.compose_db_msg("hello world"))
    server.db.add_msg_to_chat(c_id1, server.compose_db_msg("lorem ipsum"))
    print("db content: ", server.db.db.all())
    print("msgs:", server.db.get_all_msgs(c_id1, unread=True))


if __name__ == "__main__":
    main()
