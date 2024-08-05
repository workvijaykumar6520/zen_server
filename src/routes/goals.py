import json
from db_config import db
from datetime import datetime, timezone
from google.cloud import firestore
from routes.utils import extract_json, gemini_llm
from langchain_google_genai import ChatGoogleGenerativeAI
from templates.goals import GET_GOAL_RECOMMENDATION, GET_GOAL_TARGETS, MODIFIED_GET_GOAL_TARGETS
import re
import os
import google.generativeai as genai
from partialjson.json_parser import JSONParser
import google.generativeai as genai # directly importing google generative ai


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
parser = JSONParser()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-pro", google_api_key=GEMINI_API_KEY, stream=True
)

def getGoalRecommendation(questionnaireResp, user_data):
    # Convert questionnaire response to JSON string
    questionnaireResponseString = json.dumps(questionnaireResp)
    promptString = GET_GOAL_RECOMMENDATION + questionnaireResponseString

    # Invoke the Gemini LLM to get goal recommendations
    result = gemini_llm.invoke(promptString)
    if hasattr(result, 'content'):
        try:
            # Parse the result content
            data = json.loads(result.content)

            # Store each goal in Firestore and include the generated document ID in the data
            for goal in data:
                # Prepare the goal data with additional fields
                db_data = {
                    "user_id": user_data,  # User ID for whom the goal is being created
                    "goal_status": "todo",  # Status of the goal
                    "createdAt": datetime.now(timezone.utc),
                    "updatedAt": datetime.now(timezone.utc),
                    **goal,  # Copy the entire goal object
                }

                # Add each goal to the Firestore "goal" collection
                result = db.collection("goal").add(db_data)
                
                # Extract DocumentReference from the tuple
                if isinstance(result, tuple):
                    _, doc_ref = result  # Extract DocumentReference from tuple
                else:
                    doc_ref = result  # Direct DocumentReference

                # Update the document with the generated ID
                db.collection("goal").document(doc_ref.id).update({"id": doc_ref.id})

            return {"data": {}, "message": "Goals stored successfully"}

        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            return {"data": {}, "message": "Failed to decode JSON response"}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"data": {}, "message": "Unable to store the goals, please try again"}

    return {"data": {}, "message": "No content in result"}


def getGoalsByUserId(data):
  response=  db.collection("goal").where("user_id", "==", data).get()
 
  goals = [{"id": doc.id, **doc.to_dict()} for doc in response]
  print(goals,"response")
  return goals


def getGoalTargets(goal_id):
    # not using it currently we might remove this in future
    try:
        # Fetch the document from Firestore using the goal_id
        goal_doc = db.collection("goal").document(goal_id).get()
        if goal_doc.exists:
            # Convert document to a dictionary
            goal_data = goal_doc.to_dict()

            # Extract and handle the goal's long description
            goal_target_json = json.dumps(goal_data.get("longDescription", "")) or ""

            # Construct the prompt string
            promptString = goal_target_json + GET_GOAL_TARGETS
            result = gemini_llm.invoke(promptString)
            raw_content = result.content.strip()

            # Attempt to parse the JSON response
            try:
                response = extract_json(raw_content)
                try:
                    # storing the target goal in DB
                    db.collection("goal").document(goal_id).update({"goalPlan":prevResp})
                except Exception as e:
                    print("exception occurred while inserting in DB", e)

                return {
                    "success": True,
                    "data": response,
                    "message": "Goal targets fetched successfully"
                }
            except json.JSONDecodeError as json_err:
                print(f"JSON decode error: {json_err}")
                return {
                    "success": False,
                    "data": goal_data,
                    "message": "Failed to parse JSON from LLM response"
                }
        else:
            return {
                "success": True,
                "data": {},
                "message": "No such goal exists"
            }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "success": False,
            "data": {},
            "message": "Failed to fetch goal details"
        }


def streamGoalTargets(goal_id):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

    # Fetch the document from Firestore using the goal_id
    goal_doc = db.collection("goal").document(goal_id).get()
    if goal_doc.exists:
        goal_data = goal_doc.to_dict()
        goal_target_json = json.dumps(goal_data.get("longDescription", "")) or "" # need to send proper data to gemini and update the prompt

        promptString = goal_target_json + GET_GOAL_TARGETS

        response = model.generate_content(promptString, stream=True)
        prevResp = {}
        streamJson = ""
        for chunk in response:
            content = chunk.text
            if(content):
                streamJson += content
                try:
                    parsedJson = parser.parse(streamJson)
                    prevResp = parsedJson
                    yield json.dumps(parsedJson)
                except:
                    yield json.dumps(prevResp)
        try:
            # storing the target goal in DB
            db.collection("goal").document(goal_id).update({"goalPlan":prevResp})
        except Exception as e:
            print("exception occurred while inserting in DB", e)

# working code with langchain keeping this for future reference
# def streamGoalTargets(goal_id):
#     # Fetch the document from Firestore using the goal_id
#     goal_doc = db.collection("goal").document(goal_id).get()
#     if goal_doc.exists:
#         goal_data = goal_doc.to_dict()
#         goal_target_json = json.dumps(goal_data.get("longDescription", "")) or "" # need to send proper data to gemini and update the prompt

#         promptString = goal_target_json + GET_GOAL_TARGETS

#         resp = ""
#         prevResp = {}
#         for chunk in gemini_llm.stream([promptString]):
#             print("chunk", chunk)
#             resp += str(chunk.content)
#             result = extract_json(resp)
#             print("Result", result)
#             if result:
#                 prevResp = result
#                 yield json.dumps(result)
#             else:
#                 yield json.dumps(prevResp)
    
#     # store in DB here