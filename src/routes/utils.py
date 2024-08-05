import json
import os
import re
from partialjson.json_parser import JSONParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


parser = JSONParser()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-pro", google_api_key=GEMINI_API_KEY, stream=True
)

def extract_json(md_content):
    """Extracts JSON from a Markdown code block."""
    # Regular expression to match a code block containing JSON
    json_pattern_1 = r"```json\n(.*)\n"
    json_pattern_2 = r"```json\n(.*)\n```"

    match1 = re.search(json_pattern_1, md_content, re.DOTALL)
    match2 = re.search(json_pattern_2, md_content, re.DOTALL)
    json_string = ""

    if match1 or match2:
        try:
            if match2:
                json_string = match2.group(1)
            else:
                json_string = match1.group(1)
            if json_string:
                parse_resp = parser.parse(json_string)
                return parse_resp
        except json.JSONDecodeError:
            print("Error decoding JSON", md_content)
            return {}
    else:
        try:
            parse_resp = parser.parse(md_content)
            return parse_resp
        except:
            print("Error decoding JSON", md_content)
            return {}
    return {}
