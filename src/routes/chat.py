import os
from flask import jsonify
from langchain.chains import ConversationChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import messages_from_dict, messages_to_dict
from langchain.memory import ConversationSummaryMemory
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)
summary = ConversationSummaryMemory(llm=gemini_llm)

def getChatData():
    # we need to implement Python version of the below JS code variant


    # const sessionRef = db.collection('session').doc('user_id');
    # const query = sessionRef.collection('chats').where('session_id', '==', session_id);

    # query.get().then((snapshot) => {
    #     snapshot.forEach((doc) => {
    #         print(doc.id, '=>', doc.data());
    #     });
    # });
    pass


chat_obj= {}
def chat_gemini(user_message, session_id):
    retrieve_from_db = chat_obj.get(session_id, {}) or {}
    print("\n\n retrieved for user", session_id, " -> ", retrieve_from_db)

    retrieved_memory = summary
    if(retrieve_from_db):
        print("\n\nRoger", retrieve_from_db)
        retrieved_messages = messages_from_dict(retrieve_from_db["messages"])
        retrieved_summary = retrieve_from_db["conversation_summary"]
        

        entities = retrieved_memory.clear()
        print("\n\nafter entities cleared", entities)
        if(retrieved_summary):
            print("in if ", retrieved_summary)
            retrieved_memory.buffer = retrieved_summary

            entities = retrieved_memory.buffer
            print("\n\nafter adding retrieved entities", entities)

    conversation_summary_chain = ConversationChain(
        llm=gemini_llm,
        verbose=True,
        memory=retrieved_memory
    )
    conversation_summary_chain.run(user_message)
    
    extracted_messages = conversation_summary_chain.memory.chat_memory.messages

    print("\n\nextracted_messages", extracted_messages)

    print("\n\n", "retrieved_memory", retrieved_memory)
    
    # we also need to store the buffer in the DB
    conversation_summary = retrieved_memory.buffer

    # we need to store user messages in DB extracted_message in DB
    chat_obj[session_id] = { 
        "conversation_summary" : conversation_summary,
        "messages" : messages_to_dict(extracted_messages)
    }

    return {"response": chat_obj}
