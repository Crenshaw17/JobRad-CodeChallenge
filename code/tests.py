import unittest
from src.ChatServer import ChatAppServer, ChatAppDB
from tinydb import Query



class ChatServerTests(unittest.TestCase):

    def setUp(self):
        self.db = ChatAppDB()


class ChatAppDBTests(unittest.TestCase):
    def setUp(self):
        self.db = ChatAppDB("/db/test_db.json")

    def test_db_empty(self):
        assert self.db.db.all() == [], "database not empty"

    def test_db_function(self):
        testquery = Query()

        # test that chat was stored
        self.db.add_new_chat("test1")
        test1query = self.db.db.search(testquery["cid"] == "test1")
        assert len(test1query) > 0, "chat not added to db"

        # test not stored twice
        self.db.add_new_chat("test1")
        test1query = self.db.db.search(testquery["cid"] == "test1")
        self.assertEqual(len(test1query), 1, "chat added twice")

        # test that another chat was stored
        self.db.add_new_chat("test2")
        test2query = self.db.db.search(testquery["cid"] == "test2")
        assert len(test2query) > 0

        # test that 2 chat_ids are found
        chat_ids = self.db.get_all_chat_ids()
        assert len(chat_ids) == 2
        self.assertIn("test1", chat_ids, "test1 cid not found")
        self.assertIn("test2", chat_ids, "test2 cid not found")

        # test no messages yet for the chats
        self.assertEqual(len(self.db.get_all_msgs("test1")), 0, "message was found")
        self.assertEqual(len(self.db.db.search(testquery["cid"] == "test1")[0]["msgs"]), 0, "invalid message count")
        self.assertEqual(len(self.db.get_all_msgs("test2")), 0, "message was found")
        self.assertEqual(len(self.db.db.search(testquery["cid"] == "test2")[0]["msgs"]), 0, "invalid message count")

        # test correct number of messages
        self.db.add_msg_to_chat("test1", {"text" : "hello1"})
        self.assertEqual(len(self.db.db.search(testquery["cid"] == "test1")[0]["msgs"]), 1, "invalid message count")
        self.assertEqual(len(self.db.get_all_msgs("test1")), 1, "invalid message count")

        self.db.add_msg_to_chat("test2", {"text": "hello2"})
        self.assertEqual(len(self.db.db.search(testquery["cid"] == "test2")[0]["msgs"]), 1, "invalid message count")
        self.assertEqual(len(self.db.get_all_msgs("test2")), 1, "invalid message count")

        self.db.add_msg_to_chat("test1", {"text": "world"})
        self.assertEqual(len(self.db.db.search(testquery["cid"] == "test1")[0]["msgs"]), 2, "invalid message count")
        self.assertEqual(len(self.db.get_all_msgs("test1")), 2, "invalid message count")

        # check db emptied
        self.db.clear_db()
        assert self.db.db.all() == [], "database not empty"
