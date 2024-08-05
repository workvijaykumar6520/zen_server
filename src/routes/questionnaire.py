import json
from db_config import db
from partialjson.json_parser import JSONParser
from datetime import datetime, timezone
from templates.questionnaire import GET_QUESTIONNAIRE
from routes.utils import extract_json, gemini_llm
from routes.goals import getGoalRecommendation

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


def post_questionnaire(data, user_data):
    db_data = {
        "user_id": user_data,  # todo
        "questionnaire_resp": data["questionnaireResponse"],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
    try:
        doc_ref = db.collection("questionnaire").add(db_data)
        goalRecommendationResp = getGoalRecommendation(
            data["questionnaireResponse"], user_data
        )
        # todo call getGoalRecommendation function and save the data to db
        return {"data": {}, "message": "Questionnaire stored successfully"}
    except Exception as e:
        return {
            "data": {},
            "message": f"Unable to store the questionnaire: {str(e)}",
        }
