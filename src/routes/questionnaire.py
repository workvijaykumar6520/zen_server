import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from templates.questionnaire import GET_QUESTIONNAIRE
import json
import re

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)

def extract_json_from_md(md_content):
    """Extracts JSON from a Markdown code block."""
    # Regular expression to match a code block containing JSON
    json_pattern = r"```json\n(.*)\n```"

    match = re.search(json_pattern, md_content, re.DOTALL)
    if match:
        json_string = match.group(1)
        try:
            return json_string
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return None
    else:
        print("JSON not found in Markdown")
    return None

def get_questionnaire():
    template = GET_QUESTIONNAIRE
    result = gemini_llm.invoke(template)
    resp = extract_json_from_md(result.content)
    return resp