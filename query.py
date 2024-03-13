import argparse
from langchain_community.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import openai
import os
from openai import OpenAI
import json
import shutil
import fitz  # PyMuPDF

from settings import *

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name=OPEN_AI_EMBEDDING_MODEL_NAME
)
openai_client = OpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY,
)
chroma_db_client = chromadb.HttpClient(host=CHROMA_DB_SERVER_IP, port=8000)
chroma_db_collection = chroma_db_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME,
                                                                 embedding_function=openai_ef)

# PROMPT_TEMPLATE = """
# Answer the question based only on the following context:
#
# {context}
#
# ---
#
# Answer the question based on the above context: {question}
# """


# def main():
#     # Create CLI.
#     # parser = argparse.ArgumentParser()
#     # parser.add_argument("query_text", type=str, help="The query text.")
#     # args = parser.parse_args()
#     # query_text = args.query_text
#     # query_text = "Tell me about GoI FRB 2024 "
#     query_text = "What is PM Vishwakarma Scheme?"
#
#     client = chromadb.HttpClient(host='localhost', port=8000)
#     collection = client.get_collection(name="my_collection_pdf", embedding_function=openai_ef)
#
#
#     # Prepare the DB.
#
#
#     # Search the DB.
#     results = collection.query(
#         query_texts=["Tell me about how many ATMs are there?"],
#         n_results=5
#     )
#     print("Got Results")
#     print(len(results))
#     if len(results['documents'][0]) == 0:
#         print(f"Unable to find matching results.")
#         return
#
#
#
#     context_text = "\n\n---\n\n".join([doc for doc in results['documents'][0]])
#
#     prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
#     prompt = prompt_template.format(context=context_text, question="Tell me about how many ATMs are there?")
#     print(prompt)
#
#     model = ChatOpenAI()
#     response_text = model.invoke(prompt)
#
#     sources = [metadata['path'] for metadata in results['metadatas'][0]]
#     formatted_response = f"Response: {response_text}\nSources: {sources}"
#     print(formatted_response)


prompt_with_sarkar = """
Your name is Sarkar, a specialized Chat Bot developed by Sarvam AI to serve as an RBI Notification Assistant. Your primary function is to address user inquiries strictly based on the content of RBI notifications. Here’s how you’ll operate:

Focused Expertise: You possess an in-depth understanding of RBI notifications. Your responses should always be grounded in the specific context provided by these notifications.
Contextual Awareness: For each user query, ensure the context shared aligns with the RBI notification content you are designed to interpret. If there’s a mismatch or if the provided context does not enable a sufficient response, kindly inform the user that more relevant information is needed.
Maintaining Relevance: Should the conversation veer off-topic, gently steer the user back to discussions related to RBI notifications. Your goal is to keep the dialogue within the scope of your expertise.
Adaptable Interaction: While you should remain within your designated realm of RBI notifications, be prepared to adapt your responses to the flow of the conversation, ensuring they are both relevant and helpful.

"""

messages = [{"role": "system",
             "content": prompt_with_sarkar}]

messages_with_context = []


def fetch_context_from_chroma(user_new_message):
    query_texts = []
    for message_with_context in messages_with_context:
        query_texts.append(message_with_context["content"])
    query_texts.append(user_new_message)

    results = chroma_db_collection.query(
        query_texts=query_texts,
        n_results=5
    )
    print("Got Results")
    print(len(results))
    if len(results['documents'][0]) == 0:
        print(f"Unable to find matching results.")
        return ""
    context_text = "\n\n---\n\n".join([doc for doc in results['documents'][0]])
    sources_list = [metadata['path'] for metadata in results['metadatas'][0]]

    return context_text, sources_list


while input != "quit()":
    user_message = input("You: ")

    if user_message.strip().lower() == "":
        continue

    context, sources = fetch_context_from_chroma(user_message)

    messages_with_context.append({"role": "user", "content": user_message, "context": context, "sources": sources})

    user_prompt = str('{"User": "' + user_message + '", "Context": "' + context + '"}')

    messages.append({"role": "user", "content": user_prompt})

    response = openai_client.chat.completions.create(
        messages=messages,
        model="gpt-4-0125-preview", temperature=0.4
    )

    # for message in response['choices'][0]['message']:
    #     if message['role'] == 'assistant':
    #         print(message['content'])

    reply = response.choices[0].message.content

    messages = [{"role": "system",
                 "content": prompt_with_sarkar}]

    print("Sarkar:", reply)
    print("Sources:", sources)
