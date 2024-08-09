import json
from db_config import db
from datetime import datetime, timezone
from google.cloud import firestore
from routes.utils import extract_json, gemini_llm
from langchain_google_genai import ChatGoogleGenerativeAI
from templates.goals import (
    GET_GOAL_RECOMMENDATION,
    GET_GOAL_TARGETS,
)
import re
import os
import google.generativeai as genai
from partialjson.json_parser import JSONParser
import google.generativeai as genai  # directly importing google generative ai


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
parser = JSONParser()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-pro", google_api_key=GEMINI_API_KEY, stream=True
)

def getGoalRecommendation(questionnaireResp, user_id):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})


    # Convert questionnaire response to JSON string
    questionnaireResponseString = json.dumps(questionnaireResp)
    promptString = GET_GOAL_RECOMMENDATION + questionnaireResponseString

    # Invoke the Gemini LLM to get goal recommendations
    # result = gemini_llm.invoke(promptString)

    result = model.generate_content(promptString)
    if result.text:
        try:
            # Parse the result content
            data = json.loads(result.text)

            # Store each goal in Firestore and include the generated document ID in the data
            for goal in data:
                # Prepare the goal data with additional fields
                db_data = {
                    "user_id": user_id,  # User ID for whom the goal is being created
                    "goal_status": "TO_DO",  # Status of the goal
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

            return {"success": True,"data": data, "message": "Goals stored successfully"}

        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            return {"success": False,"data": {}, "message": "Failed to decode JSON response"}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"success": False,"data": {}, "message": "Unable to store the goals, please try again"}
    return {"success": False,"data": {}, "message": "No content in result"}


def getGoalsByUserId(user_id):
    response=  db.collection("goal").where("user_id", "==", user_id).get()
    goals = [{"id": doc.id, **doc.to_dict()} for doc in response]
    if goals:
        return {"success": True,"data": goals, "message": "No content in result"}
    else:
        # we make gemini call and store in DB from here
        print("making gemini call")
        questionnaire_response = db.collection("questionnaire").where("user_id", "==", user_id).get()
        questionnaire_response = [{"id": doc.id, **doc.to_dict()} for doc in questionnaire_response]

        if questionnaire_response:
            return getGoalRecommendation(questionnaire_response[0]["questionnaire_resp"], user_id)


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
                    db.collection("goal").document(goal_id).update(
                        {"goalPlan": response}
                    )
                except Exception as e:
                    print("exception occurred while inserting in DB", e)

                return {
                    "success": True,
                    "data": response,
                    "message": "Goal targets fetched successfully",
                }
            except json.JSONDecodeError as json_err:
                print(f"JSON decode error: {json_err}")
                return {
                    "success": False,
                    "data": goal_data,
                    "message": "Failed to parse JSON from LLM response",
                }
        else:
            return {"success": True, "data": {}, "message": "No such goal exists"}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"success": False, "data": {}, "message": "Failed to fetch goal details"}


def streamGoalTargets(goal_id):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        "gemini-1.5-flash", generation_config={"response_mime_type": "application/json"}
    )

    # Fetch the document from Firestore using the goal_id
    goal_doc = db.collection("goal").document(goal_id).get()
    if goal_doc.exists:
        goal_data = goal_doc.to_dict()
        goal_target_json = (
            json.dumps(goal_data.get("longDescription", "")) or ""
        )  # need to send proper data to gemini and update the prompt

        promptString = goal_target_json + GET_GOAL_TARGETS

        response = model.generate_content(promptString, stream=True)
        prevResp = {}
        streamJson = ""
        for chunk in response:
            content = chunk.text
            if content:
                streamJson += content
                try:
                    parsedJson = parser.parse(streamJson)
                    prevResp = parsedJson
                    yield json.dumps(parsedJson)
                except:
                    yield json.dumps(prevResp)
        try:
            # storing the target goal in DB
            db.collection("goal").document(goal_id).update({"goalPlan": prevResp,"goal_status":"IN_PROGRESS"})
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


def editGoalsTargets(goal_id, data):
    try:
        goal_doc = db.collection("goal").document(goal_id)
        goal_data = goal_doc.get()
        if goal_data.exists:
            goal_data_json = goal_data.to_dict()
            for i in data:
                goal_data_json["goalPlan"][i] = data[i]
            goal_doc.update(goal_data_json)
            return {"success": True, "message": "Goal updated successfully"}
        else:
            return {"success": False, "message": "Document not found"}
    except Exception as e:
        print("exception occurred while updating:", e)



def updateTaskStatus(goal_id, day_id, task_id, new_status):
    try:
        # Reference to the specific goal document
        goal_doc_ref = db.collection('goal').document(goal_id)

        # Build the path to the specific task using Firestore's field path syntax
        task_path = f'goalPlan.{day_id}.tasks.{task_id}.status'

        # Update the task's status
        goal_doc_ref.update({task_path: new_status})
        updateDayStatusIfAllTasksDone(goal_id, day_id)

        print('Task status updated successfully')
        return {"success": True, "message": ""}, 200
    except Exception as e:
        print(f'Error updating task status: {e}')
        return {"success": False, "message": "Internal server error"}, 500
    

# def updateDayStatusIfAllTasksDone(goal_id, day_id):
#     try:
#         # Reference to the specific goal document
#         goal_doc_ref = db.collection('goal').document(goal_id)

#         # Get the document snapshot
#         goal_doc = goal_doc_ref.get()
        
#         if not goal_doc.exists:
#             print('Goal document does not exist')
#             return

#         # Retrieve the data
#         goal_data = goal_doc.to_dict()
        
#         # Retrieve tasks for the specified day
#         tasks = goal_data.get('goalPlan', {}).get(day_id, {}).get('tasks', {})

#         # Check if all tasks are done
#         all_tasks_done = all(task.get('status') == 'DONE' for task in tasks.values())

#         if all_tasks_done:
#             # Update the day status to DONE
#             day_path = f'goalPlan.{day_id}.status'
#             goal_doc_ref.update({day_path: 'DONE'})
#             print('Day status updated to DONE')
#         else:
#             day_path = f'goalPlan.{day_id}.status'
#             goal_doc_ref.update({day_path: 'TO_DO'})
#             print('Not all tasks are done yet')

#     except Exception as e:
#         print(f'Error updating day status: {e}')




def updateTaskStatus(goal_id, day_id, task_id, new_status):
    try:
        # Reference to the specific goal document
        goal_doc_ref = db.collection('goal').document(goal_id)

        # Build the path to the specific task using Firestore's field path syntax
        task_path = f'goalPlan.{day_id}.tasks.{task_id}.status'

        # Update the task's status
        goal_doc_ref.update({task_path: new_status})
        # Call function to update day and goal statuses
        updateDayStatusIfAllTasksDone(goal_id)

        print('Task status updated successfully')
        return {"success": True, "message": ""}, 200
    except Exception as e:
        print(f'Error updating task status: {e}')
        return {"success": False, "message": "Internal server error"}, 500
    

def updateDayStatusIfAllTasksDone(goal_id):
    try:
        # Reference to the specific goal document
        goal_doc_ref = db.collection('goal').document(goal_id)

        # Get the document snapshot
        goal_doc = goal_doc_ref.get()
        
        if not goal_doc.exists:
            print('Goal document does not exist')
            return

        # Retrieve the data
        goal_data = goal_doc.to_dict()
        
        # Retrieve days and their statuses
        goal_plan = goal_data.get('goalPlan', {})
        
        # Check if all days are DONE
        all_days_done = True
        for day_id, day_data in goal_plan.items():
            tasks = day_data.get('tasks', {})
            all_tasks_done = all(task.get('status') == 'DONE' for task in tasks.values())
            
            if all_tasks_done:
                day_path = f'goalPlan.{day_id}.status'
                goal_doc_ref.update({day_path: 'DONE'})
                print(f'Day {day_id} status updated to DONE')
            else:
                day_path = f'goalPlan.{day_id}.status'
                goal_doc_ref.update({day_path: 'TO_DO'})
                all_days_done = False
                print(f'Not all tasks are done yet for day {day_id}')
        
        # Update the goal status if all days are DONE
        if all_days_done:
            goal_doc_ref.update({'goal_status': 'DONE'})
            print('Goal status updated to DONE')
        else:
            goal_doc_ref.update({'goal_status': 'IN_PROGRESS'})
            print('Not all days are done yet')

    except Exception as e:
        print(f'Error updating day status: {e}')