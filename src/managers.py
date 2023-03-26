import src.primitive_objects as primitive_objects


class UserManager:
    def __init__(self):
        self.current_id = 0
        self.users = dict()  # user_id: User()
        self.load_users()

    async def get_current_id(self):
        self.current_id += 1
        return self.current_id

    def load_users(self):
        # load chats from DB
        # not implemented, data is stored in class instance only
        pass

    async def add_chat(self, user_id, other_id):
        if user_id not in self.users or other_id not in self.users:
            raise RuntimeError("At least one of users doesn't exist")
        self.users[user_id].chats.append(other_id)
        self.users[other_id].chats.append(other_id)

    async def add_user(self, user_id: int):
        new_user = primitive_objects.User(user_id)
        self.users[user_id] = new_user

    async def delete_user(self, user_id: int):
        res = (user_id in self.users.keys())
        if res:
            self.users.pop(user_id)
        return res

    async def user_exists(self, user_id):
        return user_id in self.users.keys()

    async def get_user(self, user_id):
        if await self.user_exists(user_id):
            return self.users[user_id]
        return None


class ChatManager:
    def __init__(self):
        self.chats_ = dict()  # (user_id, receiver_id): chat_id
        self.load_chats()

    def load_chats(self):
        # load chats from DB
        # not implemented, data is stored in class instance only
        pass

    async def add_chat(self, user_id, receiver_id):
        self.chats_[(user_id, receiver_id)] = primitive_objects.Chat(user_id, receiver_id)
        self.chats_[(receiver_id, user_id)] = primitive_objects.Chat(receiver_id, user_id)

    async def chat_exists(self, sender_id, receiver_id):
        return (sender_id, receiver_id) in self.chats_

    async def get_chat(self, sender_id, receiver_id):
        if (sender_id, receiver_id) in self.chats_:
            return self.chats_[(sender_id, receiver_id)]
        return None

    async def process_message(self, message: primitive_objects.Message):
        self.chats_[(message.sender_id_, message.receiver_id_)].history_.append(message)
        self.chats_[(message.receiver_id_, message.sender_id_)].history_.append(message)
