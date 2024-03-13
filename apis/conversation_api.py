from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from apis.conversation import Conversation

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/message/")
async def add_message(request: Request):
    data = await request.json()
    conversation_id = data.get("conversation_id", None)
    message = data["message"]
    conversation = Conversation(conversation_id)
    conversation.save_user_message(message)
    admin_message = conversation.fetch_and_save_admin_message()
    admin_message["conversation_id"] =conversation.conversation_id
    return admin_message

