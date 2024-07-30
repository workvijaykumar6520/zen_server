import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)

def gemini_call(user_message):
    print(user_message)
    result = gemini_llm.invoke(user_message)
    print("result", result.content)
    return result.content