import time
from pydantic import BaseModel


class IncomingMessage(BaseModel):
    sender_id: int
    receiver_id: int
    text: str


class NewChat(BaseModel):
    sender_id: int
    receiver_id: int


class Message:
    def __init__(self, message: IncomingMessage):
        self.sender_id_ = message.sender_id
        self.receiver_id_ = message.receiver_id
        self.text_ = message.text
        self.message_id_ = str(str(self.sender_id_)) + ":" + str(time.time())


class Chat:
    def __init__(self, sender_id, receiver_id):
        self.sender_id_ = sender_id
        self.receiver_id_ = receiver_id
        self.history_ = list()
        self.chat_id_ = str(str(sender_id)) + ":" + str(str(receiver_id))


class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.chats = []  # list of user_id (communicators)
