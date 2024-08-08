import os
import time
from flask import jsonify
from langchain.chains import ConversationChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import messages_from_dict, messages_to_dict
from langchain.memory import ConversationSummaryMemory
from db_config import db, firestore
from constants.constants import mental_health_prompt_template

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)
conversation_summary_memory = ConversationSummaryMemory(llm=gemini_llm)

def getChatData(user_id, start_after=None, limit=999):
    """Retrieves chat data for a given user ID with pagination.

    Args:
        user_id (str): The ID of the user.
        start_after (firestore.DocumentSnapshot, optional): The document to start after.
        limit (int, optional): The number of documents to fetch.

    Returns:
        list: A list of chat documents.
    """

    chats_ref = db.collection('chat').where('user_id', '==', user_id)

    if start_after:
        chats_ref = chats_ref.start_after(start_after)

    docs = chats_ref.limit(limit).order_by('created_at', direction=firestore.Query.DESCENDING).get()

    chat_data = [doc.to_dict() for doc in docs]

    return chat_data


def chat_gemini(user_message, user_id):
    # Retrieve summary from chat_summary collection
    summary_doc_ref = db.collection('chat_summary').document(user_id)
    summary_doc = summary_doc_ref.get().to_dict()

    retrieved_summary = None
    if summary_doc:
        retrieved_summary = summary_doc['summary']

    summary = conversation_summary_memory
    if retrieved_summary:
        # Clear existing memory and set retrieved summary
        summary.clear()
        summary.buffer = retrieved_summary

    complete_prompt = f"{mental_health_prompt_template}\n\nNew Messages:\n{user_message}"

    conversation_summary_chain = ConversationChain(
        llm=gemini_llm,
        verbose=True,
        memory=summary
    )
    conversation_summary_chain.run(complete_prompt)

    extracted_messages = conversation_summary_chain.memory.chat_memory.messages

    # Update chat_summary with current conversation summary
    summary_doc_ref.set({
        'summary': summary.buffer
    }, merge=True)  # Use merge to update only the summary field

    # Store messages in chat collection (one for AI and one for human)
    chat_ref = db.collection('chat')

    chat_ref.add({
        'chat_from': 'HUMAN',
        'user_id': user_id,
        'message': user_message,
        'created_at': round(time.time() * 1000)
    })

    extracted_message = messages_to_dict(extracted_messages)

    chat_ref.add({
        'chat_from': 'AI',
        'user_id': user_id,
        'message': extracted_message[1]["data"]["content"],
        'created_at': round(time.time() * 1000)
    })
    return extracted_message[1]["data"]["content"] or ""
