import os, json

from settings import *
import chromadb.utils.embedding_functions as embedding_functions
import chromadb
from openai import OpenAI

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name=OPEN_AI_EMBEDDING_MODEL_NAME
)
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
)
chroma_db_client = chromadb.HttpClient(host=CHROMA_DB_SERVER_IP, port=8000)
chroma_db_collection = chroma_db_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME,
                                                                 embedding_function=openai_ef)
prompt_with_sarkar = """
Your name is Sarkar, a specialized Chat Bot developed by Sarvam AI to serve as an RBI Notification Assistant. Your primary function is to address user inquiries strictly based on the content of RBI notifications. Here’s how you’ll operate:

Focused Expertise: You possess an in-depth understanding of RBI notifications. Your responses should always be grounded in the specific context provided by these notifications.
Contextual Awareness: For each user query, ensure the context shared aligns with the RBI notification content you are designed to interpret. If there’s a mismatch or if the provided context does not enable a sufficient response, kindly inform the user that more relevant information is needed.
Maintaining Relevance: Should the conversation veer off-topic, gently steer the user back to discussions related to RBI notifications. Your goal is to keep the dialogue within the scope of your expertise.
Adaptable Interaction: While you should remain within your designated realm of RBI notifications, be prepared to adapt your responses to the flow of the conversation, ensuring they are both relevant and helpful.

"""


class Conversation:
    def __init__(self, conversation_id=None):
        self.json_file_path = "apis/db.json"
        self.data = self.load_json()
        if not conversation_id:
            self.conversation = self.start_conversation()
            self.conversation_id = self.conversation.get("id")
        else:
            self.conversation = self.data.get(str(conversation_id))
            self.conversation_id = self.conversation.get("id")

    def load_json(self):
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_json(self):
        try:
            with open(self.json_file_path, 'w') as file:
                json.dump(self.data, file, indent=4)
        finally:
            file.close()

    def fetch_next_conversation_id(self):
        return (self.data.get("current_conversation_id") or 0) + 1

    def start_conversation(self):
        conversation = {
            "id": self.fetch_next_conversation_id(),
            "messages": [],
            "sequence": 0,
        }
        self.data["current_conversation_id"] = conversation["id"]
        self.data[conversation["id"]] = conversation
        self.save_json()
        return conversation

    def save_user_message(self, user_message):
        message = {
            "role": "user",
            "text": user_message,
            "sequence": self.conversation["sequence"] + 1,
        }
        self.add_message_to_conversation(message)

    def fetch_and_save_admin_message(self):
        context, sources = self.fetch_context_from_chroma()

        messages_for_gpt = [{"role": "system",
                     "content": prompt_with_sarkar}]

        messages = self.conversation['messages']
        for message in messages:
            if message["role"] == "user":
                messages_for_gpt.append({"role": "user", "content": message["text"]})
            if message["role"] == "admin":
                messages_for_gpt.append({"role": "assistant", "content": message["text"]})

        response = openai_client.chat.completions.create(
            messages=messages_for_gpt,
            model="gpt-4-0125-preview", temperature=0.4
        )
        reply = response.choices[0].message.content
        admin_message = reply
        return self.save_admin_message(admin_message, context, sources)

    def fetch_context_from_chroma(self):
        query_texts = []
        messages = self.conversation['messages']
        for message in messages:
            query_texts.append(message['text'])

        results = chroma_db_collection.query(
            query_texts=query_texts,
            n_results=5
        )
        context_text = "\n\n---\n\n".join([doc for doc in results['documents'][0]])
        sources_list = [metadata['path'] for metadata in results['metadatas'][0]]
        return context_text, sources_list

    def save_admin_message(self, admin_message, context, source):
        message = {
            "role": "admin",
            "text": admin_message,
            "context": context,
            "source": source,
            "sequence": self.conversation["sequence"] + 1,
        }
        self.add_message_to_conversation(message)
        return message

    def add_message_to_conversation(self, message):
        self.conversation["messages"].append(message)
        self.conversation["sequence"] = message["sequence"]
        self.save_json()
