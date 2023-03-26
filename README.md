# Simple fastapi chat

## How to test?
```
git clone https://github.com/yasamprom/fastapichat.git
cd fastapichat/fastapichat
python -m unittest fastapichat.test
```

## How to run chat in docker?
```
git clone https://github.com/yasamprom/fastapichat.git
cd fastapichat
docker-compose up
```

## How to run chat on local machine?
```
git clone https://github.com/yasamprom/fastapichat.git
pip install requirements.txt
cd fastapichat
uvicorn fastapichat.main:app --reload
```

## Docs

We have few objects: User, Chat, Message. They are managed by UserManager and ChatManager. Here is the list of methods.
* ### Register user
    Generate personal id for new user and return it.
    ```
    curl -X POST  http://127.0.0.1:8000/user/register
    
  response: 
        {"user_id": int}
    ```

* ### Get user's data
    Returns list of user's contacts (chats)
     ```
    curl -X GET  http://127.0.0.1:8000/user/{user_id}
  
    response: 
        200, {"user": user_id, "chats": []}
        404, user not found
    ```
 
* ### Delete user
     ```
    curl -X DELETE  http://127.0.0.1:8000/user/{user_id}
  
    response: 
        200, {"deleted": user_id}
        404, user not found
    ```

* ### Start chat
     ```
    curl -H "Content-Type: application/json" -X POST -d '{"sender_id":"1", "receiver_id":"2"}' http://127.0.0.1:8000/chat/start
    response: 
        200, {"chat_id": string}
        404, at least one of users not found
        405, chat exists
    ```

* ### Send message
     ```
    curl -H "Content-Type: application/json" -X POST -d '{"sender_id":"1", "receiver_id":"2", "text":"Hello user 2"}' http://127.0.0.1:8000/messages/send

    response: 
        200, {"message_id": string}
        404, chat was not created
    ```
* ### Get chat history
     ```
    curl -X GET 'http://127.0.0.1:8000/chat/history?sender_id=1?receiver_id=2'
  
    response: 
        200, {"messages": []}
        404, chat was not found
    ```
