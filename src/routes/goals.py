import json
from db_config import db
from datetime import datetime, timezone
from google.cloud import firestore
from routes.utils import extract_json, gemini_llm
from templates.goals import GET_GOAL_RECOMMENDATION, GET_GOAL_TARGETS,MODIFIED_GET_GOAL_TARGETS
import re
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
from partialjson.json_parser import JSONParser

parser = JSONParser()





# def getGoalRecommendation(questionnaireResp, user_data):
#     # Assuming the commented code is relevant for future use.
#     # questionnaireCollection = db.collection("questionnaire")
#     # query = questionnaireCollection.order_by(
#     #     "updatedAt", direction=firestore.Query.DESCENDING
#     # ).limit(1)
#     # results = query.stream()
#     # documents = [doc.to_dict() for doc in results]
#     # questionnaireResponse = documents[0].get("questionnaire_resp")

#     questionnaireResponseString = json.dumps(questionnaireResp)
#     promptString = GET_GOAL_RECOMMENDATION + questionnaireResponseString

#     result = gemini_llm.invoke(promptString)
#     print(result,"resul")

#     if hasattr(result, 'content'):
#         try:
#             data = json.loads(result.content)
#             print(data)
#             db_data = {
#                 "user_id": user_data,  # todo
#                 "goal_status": "todo",
#                 "goalRecommendation": data,
#                 # "createdAt": datetime.now(timezone.utc),
#                 # "updatedAt": datetime.now(timezone.utc),
#             }
#             doc_ref = db.collection("goal").add(data)
#             return {"data": {}, "message": "Questionnaire stored successfully"}
#         except json.JSONDecodeError as e:
#             print(f"Failed to decode JSON: {e}")
#             # Handle the error or return an appropriate response
#         except Exception as e:
#             return {
#                 "data": {},
#                 "message": "Unable to store the questionnaire, please try again",
#             }
    
   



import json
from datetime import datetime, timezone
from google.cloud import firestore

def getGoalRecommendation(questionnaireResp, user_data):
    # Convert questionnaire response to JSON string
    questionnaireResponseString = json.dumps(questionnaireResp)
    promptString = GET_GOAL_RECOMMENDATION + questionnaireResponseString

    # Invoke the Gemini LLM to get goal recommendations
    result = gemini_llm.invoke(promptString,)
    print(result, "result")

    if hasattr(result, 'content'):
        try:
            # Parse the result content
            data = json.loads(result.content)
            print(data)

            # Initialize Firestore client
            # db = firestore.Client()

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
  # todo get the goals by user id and return the response
  return responsex


# def getGoalTargets(data):
#     resp = ""
#     prevResp = {}
#     goalData=db.collection("goal").document(data).get()
#     print(goalData,"goalData")
#     goalTargetJson = json.dumps(data["selectedGoal"]["shortDescription"]) or ""
#     # todo FE will provide userId, and goal, fetch that json using id and get the response from gemini and steam the response
#     # and store the response to db here
#     promptString = goalTargetJson + GET_GOAL_TARGETS
#     print(promptString)
#     for chunk in gemini_llm.stream(promptString):
#         resp += str(chunk.content)
#         result = extract_json(resp)
#         if result:
#             prevResp = result
#             # todo store total goal in db
#             yield json.dumps(result)
#         else:
#             yield json.dumps(prevResp)



import json
from google.cloud import firestore

def getGoalTargets(goal_id):
    # Initialize Firestore client
    # db = firestore.Client()def getGoalTargets(goal_id):
    # Initialize Firestore client
    # db = firestore.Client()
    
    try:
        # Fetch the document from Firestore using the goal_id
        goal_doc = db.collection("goal").document(goal_id).get()

        model = genai.GenerativeModel('gemini-1.5-flash',
                              # Set the `response_mime_type` to output JSON
                              generation_config={"response_mime_type": "application/json"})
        
        prompt = """
  List 5 popular cookie recipes.
  Using this JSON schema:
    Recipe = {"recipe_name": str}
  Return a `list[Recipe]`
  """

        response = model.generate_content(prompt)
        print(response.text,"responsedwdw")

        if goal_doc.exists:
            # Convert document to a dictionary
            goal_data = goal_doc.to_dict()
            print("Goal Data:", goal_data)

            # Extract and handle the goal's long description
            goal_target_json = json.dumps(goal_data.get("longDescription", "")) or ""
            print("Goal Target JSON:", goal_target_json)

            # Construct the prompt string
            promptString = goal_target_json + MODIFIED_GET_GOAL_TARGETS
            result = gemini_llm.invoke(promptString)
            raw_content = result.content.strip()
            parse_resp = parser.parse(raw_content)
            response = re.sub(r'(?<!\\)"', r'\\"', raw_content)
            print("Raw LLM Result Content:", extract_json(raw_content),parse_resp)

            # Check if result.content is empty or invalid
            if not raw_content.strip():
                return {
                    "data": goal_data,
                    "message": "LLM returned an empty or invalid response"
                }

            # Attempt to parse the JSON response
            try:
                print("Raw JSON Data:", fix_json(response))
                data=[]
                # data = json.loads( raw_content)
                print("Parsed JSON Data:", data)
                return {
                    "data": fix_json(raw_content),
                    "message": "Goal targets fetched successfully"
                }
            except json.JSONDecodeError as json_err:
                print(f"JSON decode error: {json_err}")
                return {
                    "data": goal_data,
                    "message": "Failed to parse JSON from LLM response"
                }

        else:
            return {
                "data": {},
                "message": "No such goal exists"
            }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "data": {},
            "message": "Failed to fetch goal details"
        }




def fix_json(json_string):
    # Attempt to load the JSON data
    try:
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        # Print the error for debugging
        print(f"JSON decode error: {e}")

        # Example of fixing common issues:
        # Here, you would replace problematic parts with valid JSON.
        # For demonstration, let's assume we replace incorrect quotes.
        fixed_json_string = json_string.replace('“', '"').replace('”', '"')
        
        # Try loading the fixed JSON string
        try:
            data = json.loads(fixed_json_string)
            return data
        except json.JSONDecodeError as e:
            print(f"Fixed JSON decode error: {e}")
            return None