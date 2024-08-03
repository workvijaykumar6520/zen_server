import json
from db_config import db
from partialjson.json_parser import JSONParser
from datetime import datetime, timezone
from templates.questionnaire import GET_QUESTIONNAIRE
from routes.utils import extract_json, gemini_llm

parser = JSONParser()


def get_questionnaire():
    template = GET_QUESTIONNAIRE
    resp = ""
    prevResp = {}
    for chunk in gemini_llm.stream(template):
        resp += str(chunk.content)
        result = extract_json(resp)
        if result:
            prevResp = result
            yield json.dumps(result)
        else:
            yield json.dumps(prevResp)


def post_questionnaire(data):
    print(data)
    db_data = {
        "user_id": "123",  # todo
        "questionnaire_resp": data["questionnaireResponse"],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
    try:
        doc_ref = db.collection("questionnaire").add(db_data)
        return {"data": {}, "message": "Questionnaire stored successfully"}
    except:
        return {
            "data": {},
            "message": "Unable to stored the questionnaire, please try again",
        }
