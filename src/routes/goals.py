import json
from db_config import db
from google.cloud import firestore
from routes.utils import extract_json, gemini_llm
from templates.goals import GET_GOAL_RECOMMENDATION, GET_GOAL_TARGETS


def getGoalRecommendation():
    questionnaireCollection = db.collection("questionnaire")
    query = questionnaireCollection.order_by(
        "updatedAt", direction=firestore.Query.DESCENDING
    ).limit(1)
    results = query.stream()
    documents = [doc.to_dict() for doc in results]
    questionnaireResponse = documents[0].get("questionnaire_resp")

    questionnaireResponseString = json.dumps(questionnaireResponse)
    promptString = GET_GOAL_RECOMMENDATION + questionnaireResponseString
    resp = ""
    prevResp = {}
    for chunk in gemini_llm.stream(promptString):
        resp += str(chunk.content)
        result = extract_json(resp)
        if result:
            prevResp = result
            yield json.dumps(result)
        else:
            yield json.dumps(prevResp)
    return


def getGoalTargets(data):
    resp = ""
    prevResp = {}
    goalTargetJson = json.dumps(data["selectedGoal"]["shortDescription"])

    promptString = goalTargetJson + GET_GOAL_TARGETS
    print(promptString)
    for chunk in gemini_llm.stream(promptString):
        resp += str(chunk.content)
        result = extract_json(resp)
        if result:
            prevResp = result
            # todo store total goal in db
            yield json.dumps(result)
        else:
            yield json.dumps(prevResp)
