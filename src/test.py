import asyncio
import random
import string

from starlette.testclient import TestClient

from main import app
import unittest


class TestSimpleGet(unittest.TestCase):
    def test0_root(self):
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, it is root of this simple messenger"}


class TestRegister(unittest.TestCase):
    def test1_register(self):
        # register one user
        client = TestClient(app)
        response = client.post("/user/register")
        assert response.status_code == 200
        assert response.json() == {"user_id": 1}

    def test2_empty_chat(self):
        # register user and assert chat list is empty
        client = TestClient(app)
        response = client.post("/user/register")
        assert response.status_code == 200
        assert response.json() == {"user_id": 2}
        response = client.get("/user/1")
        assert response.status_code == 200
        assert response.json() == {"user": 1, "chats": []}

    def test3_fake_user(self):
        # get fake user
        client = TestClient(app)
        response = client.get("/user/3")
        assert response.status_code == 404


class TestRegisterAndCreateChat(unittest.TestCase):
    def test1_empty_chat(self):
        client = TestClient(app)
        # register 3 users
        for i in range(3):
            client.post("/user/register")
        # start chat 1 -> 2
        response = client.post("/chat/start", json={"sender_id": 1, "receiver_id": 2})
        assert response.status_code == 200
        assert response.json() == {'chat_id': '(1, 2)'}

        # try to start chat 2 -> 1
        response = client.post("/chat/start", json={"sender_id": 2, "receiver_id": 1})
        # assert chat already exists
        assert response.status_code == 405

        # start chat 1 -> 100 and it should be failed
        response = client.post("/chat/start", json={"sender_id": 1, "receiver_id": 100})
        assert response.status_code == 404

    def test2_chat_history(self):
        client = TestClient(app)
        response = client.get("/chat/history", params={"sender_id": 1, "receiver_id": 2})
        assert response.status_code == 200
        assert response.json() == {"messages": []}

    def test3_send_message(self):
        client = TestClient(app)
        # send 2 messages
        response = client.post("/messages/send", json={"sender_id": 1, "receiver_id": 2, "text": "hello"})
        assert response.status_code == 200

        response = client.post("/messages/send", json={"sender_id": 1, "receiver_id": 2, "text": "buy"})
        assert response.status_code == 200

        # assert all messages are in chat history
        response = client.get("/chat/history", params={"sender_id": 1, "receiver_id": 2})
        assert response.status_code == 200
        assert len(response.json()["messages"]) == 2
        assert response.json()["messages"][0]['text_'] == "hello"
        assert response.json()["messages"][1]['text_'] == "buy"

        # chat for 2 user should be same as for 1 user
        response = client.get("/chat/history", params={"sender_id": 2, "receiver_id": 1})
        assert response.status_code == 200
        assert len(response.json()["messages"]) == 2
        assert response.json()["messages"][0]['text_'] == "hello"
        assert response.json()["messages"][1]['text_'] == "buy"


class TestRegisterAndDelete(unittest.TestCase):
    def test1_empty_chat(self):
        client = TestClient(app)
        # register 3 users
        created = []
        for i in range(3):
            response = client.post("/user/register")
            assert response.status_code == 200
            created.append(response.json()["user_id"])
        # delete 3 users and make sure we can't access them
        for i in range(3):
            response = client.delete("/user/" + str(created[i]))
            assert response.status_code == 200
            response = client.get("/user/" + str(created[i]))
            assert response.status_code == 404


async def register(client):
    response = client.post("/user/register")
    assert response.status_code == 200


async def send(client, from_id, to_id, text):
    response = client.post("/messages/send", json={"sender_id": from_id, "receiver_id": to_id, "text": text})
    assert response.status_code == 200


def get_message(n):
    # yields random message
    cnt = 1
    while cnt < n:
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(50))
        yield result_str
        n += 1


class TestRegisterAndCreateChatManyTimes(unittest.TestCase):
    def test1_register_many(self):
        client = TestClient(app)
        tasks = [register(client) for i in range(100)]
        asyncio.gather(*tasks)

    def test2_send_many(self):
        NUM_MESSAGES = 500
        client = TestClient(app)

        client.post("/user/register")
        client.post("/user/register")
        response = client.post("/chat/start", json={"sender_id": 5, "receiver_id": 6})
        assert response.status_code == 200

        # create NUM_PAGES tasks to send message
        generator = get_message(NUM_MESSAGES)
        tasks = [send(client, 5, 6, next(generator)) for i in range(NUM_MESSAGES)]

        # start tasks and wait until they are completed
        loop = asyncio.get_event_loop()
        group = asyncio.gather(*tasks)
        loop.run_until_complete(group)
        loop.close()

        # assert all messages are delivered and both of communicators have same history
        response1 = client.get("/chat/history", params={"sender_id": 5, "receiver_id": 6})
        response2 = client.get("/chat/history", params={"sender_id": 6, "receiver_id": 5})
        assert response1.status_code == 200 and response2.status_code == 200
        assert len(response1.json()["messages"]) == NUM_MESSAGES
        assert response1.json() == response2.json()
