import datetime
from Messages import BaseMessage, SenderType, compose_msg, chat_json_to_basemessages
from enum import Enum
from rich.prompt import Prompt
import rich as r
import time
import requests


# function to choose the appropriate chat mode and return chat client object
def choose_chat_mode(k):
    # build cli with user select
    ui = r.console.Console()
    ui.print(r.padding.Padding("Welcome to the ChatClientApp", (2, 4)), style="bold")

    while True:
        ui.print("Please select the ChatClient role:\n\n  <1> -> client mode\n  <2> -> customer service mode\n")
        mode = r.prompt.Prompt.ask(">>")
        if mode == "1":
            return CustomerChatClient(ui=ui)
        elif mode == "2":
            return ServiceChatClient(ui=ui)
        else:
            continue
    return None


# base class for chat client CLI application
class ChatClientBase():

    def __init__(self, ui=None):
        self.chatmode = SenderType.NOTDEFINED
        self.ui = ui

    # virtual method
    def chat_runtime(self):
        return

    # API call to send a message, create a transmittable message object before
    def send_msg(self, m: str, sender_type: SenderType, sender_name: str, chat_id: str):
        msg = compose_msg(m, chat_id, sender_type, sender_name)
        # the API call has to go to the docker container hostname on port 8080
        response = requests.put("http://chatserver:8080/chats/{:s}".format(chat_id),
                                data=msg.model_dump_json(), headers={"Content-Type": "application/json"})
        if response.ok:
            self.ui.print("  message sent!\n", style="italic")
        else:
            self.ui.print("  message failed to send! :/\n", style="bold black on white italic")

    # method for handling user chat input and sending to server via REST API
    def write_chat_msg(self, chat_id, chatter_name=""):
        self.ui.print("\n")
        self.ui.print(
            "[black on white bold]-> Write your message below[/black on white bold] | Send with <ENTER>:")
        msg = r.prompt.Prompt.ask("\n( [i green]{:s}[/i green] )".format(chatter_name))
        self.ui.print("\n")
        self.send_msg(msg, self.chatmode, chatter_name, chat_id)

    # API call to retrieve message from server
    # RETURNS: True  -> if chat exists
    #          False -> if chat not found
    #        + list[BaseMessage]
    def display_existing_chat(self, chat_id: str, refreshed=False):
        chat_response = requests.get("http://chatserver:8080/chats/{:s}".format(chat_id))
        base_msgs = []
        if chat_response.ok:
            base_msgs = chat_json_to_basemessages(chat_response.json())
        # build ui
        return self.display_chat_history(base_msgs, chat_id, refreshed), base_msgs

    # ask the user to provide a chat_id to retrieve a chat
    def get_chat_id_fromuser(self):
        self.ui.print(r.padding.Padding("\nPlease type in the chat_id of the existing chat\n", (0, 5)), style="bold")
        chat_id = r.prompt.Prompt.ask(">> chat_id")
        return chat_id

    # ask the user to provide a name
    def get_chattername(self):
        self.ui.print(r.padding.Padding("What's your name?", (1, 5)), style="bold")
        chatter_name = r.prompt.Prompt.ask(">>")
        return chatter_name

    # display all messages up-to-now
    # RETURNS: True  -> if chat exists
    #          False -> if chat not found
    def display_chat_history(self, msgs, chat_id="", refreshed=False):
        if len(msgs) > 0:
            self.ui.print("\n")
            self.ui.rule("[blue]history for chat [bold]#{:s}[/bold]".format(chat_id))
            self.ui.print("\n")
            for msg in msgs:
                self.display_msg(msg)
            if refreshed:
                self.ui.print("refreshed on {:s}\n".format(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")),
                              justify="center", style="italic")
            return True
        else:
            self.ui.print("\n")
            self.ui.rule()
            self.ui.print("no chat history found for chat_id {:s}!".format(chat_id),
                          style="bold italic", justify="center")
            self.ui.print("\n")
        return False

    # display a simple message in the terminal
    def display_msg(self, msg: BaseMessage):
        disp_side = "left"
        if (msg.sender_type == SenderType.CLIENT.value
            and self.chatmode.value == SenderType.CLIENT.value) or (
                msg.sender_type == SenderType.CUSTOMER_SERVICE.value
                and self.chatmode.value == SenderType.CUSTOMER_SERVICE.value):
            disp_side = "right"

        msg_table = r.table.Table(
            title="  {:s}".format(datetime.datetime.fromtimestamp(msg.timestamp).strftime("%m/%d/%Y, %H:%M:%S")),
            min_width=40,
            title_justify=disp_side)
        msg_table.add_column("{:s} wrote".format(msg.sender_name), style="green", max_width=60)
        msg_table.add_row(msg.msg)
        self.ui.print(msg_table, justify=disp_side)
        self.ui.print("---", justify="center")
        return

    # display chat loop for opened chat
    def display_chat_loop(self, chat_id: str, chatter_name: str):
        self.ui.print("-> select action:\n", style="bold black on white")
        self.ui.print(r.padding.Padding("<m> -> write a new message in the chat", (0, 3)), justify="left")
        self.ui.print(r.padding.Padding("<r> -> refresh the chat", (0, 3)), justify="left")
        if self.chatmode == SenderType.CUSTOMER_SERVICE:
            self.ui.print(r.padding.Padding("<q> -> return to chat list", (0, 3)), justify="left")
        else:
            self.ui.print(r.padding.Padding("<q> -> exit chat", (0, 3)), justify="left")

        mode = r.prompt.Prompt.ask("\n>> action")

        if mode == "m":
            # write new message
            self.write_chat_msg(chat_id, chatter_name)
            self.ui.print("  -> refreshing shortly...\n")
            time.sleep(1.5)
            self.display_existing_chat(chat_id, refreshed=True)
            return True
        elif mode == "r":
            # refresh the chat window
            print("-> Refreshing...\n")
            self.display_existing_chat(chat_id, refreshed=True)
            return True
        elif mode == "q":
            # quit app
            if self.chatmode == SenderType.CLIENT:
                print("-> Quitting. Thanks! :)")
            else:
                self.ui.rule("chat exited")
            return False
        else:
            print("-> action not implemented!")
            return True


# a customer chat CLI interface
class CustomerChatClient(ChatClientBase):
    def __init__(self, ui):
        super().__init__(ui=ui)
        self.chatmode = SenderType.CLIENT
        self.ui.print("\n")
        ui.rule("[bold blue]CLIENT MODE")

    # main client ui routine
    def chat_runtime(self):
        self.ui.print(r.padding.Padding("\n-> Do you want to start a new chat or continue an existing one?", (0, 5)), style="bold")

        while True:
            self.ui.print("\n  <1> -> new chat \n  <2> -> existing chat\n  <3> -> exit\n")
            mode = r.prompt.Prompt.ask(">>")

            chat_id = ""
            chatter_name = ""
            if mode == "1":
                chat_id, chatter_name = self.new_chat()
                self.display_existing_chat(chat_id)
                break
            elif mode == "2":
                chat_id = self.get_chat_id_fromuser()
                chat_exists, base_msgs = self.display_existing_chat(chat_id)
                if chat_exists:
                    chatter_name = base_msgs[0].sender_name
                break
            elif mode == "3":
                self.ui.print("  -> exiting. Thanks! :)", style="italic")
                return
            else:
                continue

        # enter chat loop as long as no quit signal is received
        while self.display_chat_loop(chat_id, chatter_name):
            continue

    # API call to create a new chat on the server and enter chat ui routine
    def new_chat(self):
        new_chat_id = None
        self.ui.print("  -> creating new chat", style="italic")

        # get new chat_id from server
        response = requests.get("http://chatserver:8080/chats/newchat")
        if response.ok:
            new_chat_id = response.json()
            self.ui.print(r.padding.Padding("  -> Your chat_id is: [bold]{:s}[/bold]".format(new_chat_id), (1, 0)), style="italic")
        else:
            self.ui.print(">> Failed to create a new chat on the server!")
            return "", ""
        chatter_name = self.get_chattername()

        # enter chat ui context
        self.write_chat_msg(new_chat_id, chatter_name)
        return new_chat_id, chatter_name


# customer service chat client mode
class ServiceChatClient(ChatClientBase):
    def __init__(self, ui):
        super().__init__(ui=ui)
        self.chatmode = SenderType.CUSTOMER_SERVICE
        self.ui.print("\n")
        ui.rule("[bold blue]CUSTOMER SERVICE MODE")

    # main ui routine
    def chat_runtime(self):
        self.ui.print(r.padding.Padding("\n-> Do you want to display all chats or continue an existing one?", (0, 5)),
                      style="bold")

        while True:
            self.ui.print("\n-> select action:\n", style="bold black on white")
            self.ui.print("  <1> -> list all chats \n  <2> -> continue specific chat\n  <3> -> exit\n")
            mode = r.prompt.Prompt.ask(">>")
            chat_id = ""
            chatter_name = ""
            if mode == "1":
                # display all chats that are available
                self.list_all_chats()
            elif mode == "2":
                # open specific chat
                self.display_existing_chat_loop()
            elif mode == "3":
                # quit app
                self.ui.print("  -> exiting. Thank you! :)\n", style="italic")
                break
            else:
                continue

    # gets an existing chat from the server and enters the chat ui loop
    def display_existing_chat_loop(self):
        # only responding to client messages implemented, so ask for customer service name each time
        chat_id = self.get_chat_id_fromuser()
        chatter_name = self.get_chattername()
        self.ui.print("  -> retrieving chat...\n", style="italic")
        time.sleep(1.0)
        self.display_existing_chat(chat_id)
        while self.display_chat_loop(chat_id, chatter_name):
            continue

    # API request to get all existing chats from the server and displays
    def list_all_chats(self):
        chats = []
        chats_response = requests.get("http://chatserver:8080/chats")
        base_chats = []
        if chats_response.ok:
            chats = chats_response.json()
            for chat in chats:
                base_chats.append(chat_json_to_basemessages(chat[list(chat.keys())[0]]))
        # build ui
        self.ui.rule("all available chats")
        self.display_all_chats(base_chats)

    # ui function for all retrieved chats
    def display_all_chats(self, base_chats):
        chats_table = r.table.Table(title="all customer chats")
        chats_table.add_column("#", style="green")
        chats_table.add_column("name")
        chats_table.add_column("chat_id")
        #msg_table.add_row(msg.msg)

        i = 1
        for chat in base_chats:
            if len(chat) > 0:
                sender_name = chat[0].sender_name
                chat_id = chat[0].chat_id
                chats_table.add_row("{:d}".format(i), sender_name, chat_id)
                i += 1
        self.ui.print("\n")
        self.ui.print(chats_table)


if __name__ == "__main__":
    chatclient = choose_chat_mode(1)
    chatclient.chat_runtime()
