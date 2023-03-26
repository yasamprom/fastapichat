from fastapi import FastAPI, HTTPException

import src.managers as managers
import src.primitive_objects as primitive_objects


app = FastAPI()

cm = managers.ChatManager()
um = managers.UserManager()


@app.get("/")
async def root():
    """
    Greeting
    :return:
    """
    return {"message": "Hello, it is root of this simple messenger"}


@app.get("/chat/history")
async def get_chat(sender_id: int, receiver_id: int):
    """
    :param sender_id: sender
    :param receiver_id: receiver
    :return: json with chat history or 404
    """
    if await cm.chat_exists(sender_id, receiver_id):
        res = {"messages": []}
        chat = await cm.get_chat(sender_id, receiver_id)
        for message in chat.history_:
            res["messages"].append(message)
        return res
    raise HTTPException(status_code=404, detail="Chat was not found")


@app.get("/user/{user_id}")
async def get_chats(user_id: int):
    """
    Returns user's chats
    :param user_id: id of user
    :return: list of chats or 404
    """
    user = await um.get_user(user_id)
    if user:
        res = {"user": user_id, "chats": []}
        for friend_id in user.chats:
            res["chats"].append(friend_id)
        return res
    raise HTTPException(status_code=404, detail="User doesn't exist")


@app.delete("/user/{user_id}")
async def delete_user(user_id: int):
    """
    Deletes user
    :param user_id: id of user
    :return: list of chats or 404
    """
    deleted = await um.delete_user(user_id)
    if deleted:
        return {"deleted": user_id}
    raise HTTPException(status_code=404, detail="User doesn't exist")


@app.post("/user/register")
async def register_user():
    """
    Generate new unique id and registers new user
    :return: json with generated user_id
    """
    new_user_id = await um.get_current_id()
    await um.add_user(new_user_id)
    return {"user_id": new_user_id}


@app.post("/chat/start")
async def start_chat(new_chat: primitive_objects.NewChat):
    """
    Starts chat between two users
    :param new_chat: class containing two communicators
    :return: generated chat id or 404 if user doesn't exist or 405 if chat exists
    """
    sender_id = new_chat.sender_id
    receiver_id = new_chat.receiver_id
    if await cm.chat_exists(sender_id, receiver_id):
        raise HTTPException(status_code=405, detail="Chat exist")
    if not await um.user_exists(sender_id) or not await um.user_exists(receiver_id):
        raise HTTPException(status_code=404, detail="At least one of users not found")
    await cm.add_chat(sender_id, receiver_id)
    await um.add_chat(sender_id, receiver_id)
    return {"chat_id": str((sender_id, receiver_id))}


@app.post("/messages/send")
async def create_message(new_message: primitive_objects.IncomingMessage):
    """
    Delivers message
    :param new_message: Message object
    :return: json with message_id or 404
    """
    sender_id = new_message.sender_id
    receiver_id = new_message.receiver_id
    if not await cm.chat_exists(sender_id, receiver_id):
        raise HTTPException(status_code=404, detail="Chat doesn't exist")
    message = primitive_objects.Message(new_message)
    await cm.process_message(message)
    return {"message_id": message.message_id_}
