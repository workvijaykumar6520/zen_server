import json
from db_config import db
from datetime import datetime, timezone
from google.cloud import firestore
from routes.utils import extract_json, gemini_llm
from templates.goals import GET_GOAL_RECOMMENDATION, GET_GOAL_TARGETS


def getGoalRecommendation(questionnaireResp, user_data):
    # questionnaireCollection = db.collection("questionnaire")
    # query = questionnaireCollection.order_by(
    #     "updatedAt", direction=firestore.Query.DESCENDING
    # ).limit(1)
    # results = query.stream()
    # documents = [doc.to_dict() for doc in results]
    # questionnaireResponse = documents[0].get("questionnaire_resp")

    questionnaireResponseString = json.dumps(questionnaireResp)
    promptString = GET_GOAL_RECOMMENDATION + questionnaireResponseString

    result = gemini_llm.invoke(promptString)
    data = json.loads(result)
    print(data)
    db_data = {
        "user_id": user_data,  # todo
        "goal_status": "todo",
        "goalRecommendation": data,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
    try:
        doc_ref = db.collection("goal").add(db_data)
        return {"data": {}, "message": "Questionnaire stored successfully"}
    except:
        return {
            "data": {},
            "message": "Unable to stored the questionnaire, please try again",
        }
    # save the data to db

    # resp = ""
    # prevResp = {}
    # for chunk in gemini_llm.stream(promptString):
    #     resp += str(chunk.content)
    #     result = extract_json(resp)
    #     if result:
    #         prevResp = result
    #         yield json.dumps(result)
    #     else:
    #         yield json.dumps(prevResp)
    return


# todo new function for getGaolRecommendation


def getGoalTargets(data):
    resp = ""
    prevResp = {}
    goalTargetJson = json.dumps(data["selectedGoal"]["shortDescription"]) or ""
    # todo FE will provide userId, and goal, fetch that json using id and get the response from gemini and steam the response
    # and store the response to db here
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
