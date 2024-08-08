from flask import Flask, request, Response, stream_with_context, jsonify
from flask_cors import cross_origin
import logging
from dotenv import load_dotenv
from db_config import auth_service

load_dotenv(".env")
from flask import request
from routes.health import health
from routes.gemini import gemini_call
from routes.users import user_call
from routes.questionnaire import get_questionnaire
from routes.questionnaire import post_questionnaire
from routes.goals import (
    getGoalRecommendation,
    getGoalTargets,
    getGoalsByUserId,
    streamGoalTargets,
    editGoalsTargets,
    updateTaskStatus
)
from routes.login import login_with_google
from routes.dashboard import get_user_goals_progress,get_motivational_quote
from auth_config import decodeAuth

# Note :- THIS FILE SHOULD ONLY CONTAIN ROUTING AND LOGGING

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)


@app.route("/api/health")
@cross_origin()
def health_route():
    try:
        logging.info("/api/health api called")
        healthResponse = health()
        return {"message": healthResponse}, 201
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500


# @app.route("/api/gemini", methods=["POST"])
# @cross_origin()
# def _gemini_call_():
#     try:
#         logging.info("/api/gemini api called")
#         data = request.get_json()
#         print(request.headers,"headers")
#         user_message = data.get("message")
#         user_id = data.get("user_id")
#         gemini_call_resp = gemini_call(user_message)
#         return {"gemini_call_resp": gemini_call_resp}, 200
#     except Exception as e:
#         logging.error(e, exc_info=True)
#         return {"success": False, "message": "Internal server error"}, 500


@app.route("/api/login", methods=["POST"])
def login():
    try:
        # Get the ID token from the request
        id_token = request.json["idToken"]

        # Verify the ID token and retrieve user info
        user_info = login_with_google(id_token)

        if user_info:
            return jsonify({"status": "success", "user": user_info.email}), 200
        else:
            return jsonify({"status": "failed"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/gemini", methods=["POST"])
@cross_origin()
def _gemini_call_():
    try:
        logging.info("/api/gemini api called")
        data = request.get_json()
        print(request.headers, "headers")

        # Retrieve the token from the Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # Verify the token using Firebase Authentication
                decoded_token = auth_service.verify_id_token(token)
                user_id = decoded_token["uid"]
                logging.info(f"Token verified for user: {user_id}")
            except Exception as e:
                logging.error(f"Token verification failed: {e}")
                return {"success": False, "message": "Invalid or expired token"}, 401
        else:
            return {
                "success": False,
                "message": "Authorization token missing or invalid",
            }, 401

        user_message = data.get("message")
        gemini_call_resp = gemini_call(user_message)
        return {"gemini_call_resp": gemini_call_resp}, 200
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500


@app.route("/api/user", methods=["POST"])
@cross_origin()
def users():
    try:
        logging.info("/api/users api called")
        data = request.get_json()
        user_status = user_call(data)
        return {"users_call_resp": user_status}, 200
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500


@app.route("/api/questionnaire", methods=["GET"])
@cross_origin()
def getQuestionnaire():
    try:
        logging.info("/api/questionnaire api called")
        return Response(
            stream_with_context(get_questionnaire()), content_type="application/json"
        )
        # return {"success": True, "data": questionnaireStatus, "message": "Successfully generated questionnaire"}
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500


@app.route("/api/questionnaire", methods=["POST"])
@cross_origin()
def saveQuestionnaire():
    try:
        logging.info("/api/questionnaire POST api called")
        data = request.get_json()
        print(data)
        authResponse = decodeAuth(request.headers)
        if isinstance(authResponse, tuple):
            auth_data, status_code = authResponse
            if not auth_data["success"]:
                return auth_data, status_code
        else:
            auth_data = authResponse
            if not auth_data["success"]:
                return auth_data, 401

        user_data = auth_data.get("data")
        if not user_data:
            return {"success": False, "message": "User data not found"}, 400

        response = post_questionnaire(data, authResponse["data"])
        return {"questionnaire_response": response}, 200
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500


@app.route("/api/goal-recommendation", methods=["GET"])
@cross_origin()
def goalRecommendation():
    try:
        logging.info("/api/goal-recommendation GET called")
        authResponse = decodeAuth(request.headers)

        if isinstance(authResponse, tuple):
            auth_data, status_code = authResponse
            if not auth_data["success"]:
                return auth_data, status_code
        else:
            return getGoalsByUserId(authResponse["data"])
            auth_data = authResponse
            if not auth_data["success"]:
                return auth_data, 401

        # return Response(
        #     stream_with_context(getGoalRecommendation()),
        #     content_type="application/json",
        # )

    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500


@app.route("/api/goal-targets", methods=["GET"])
@cross_origin()
def weekGoals():
    try:
        logging.info("/api/goal-targets GET called")
        goal_id = request.args.get("goal_id")
        goalTargetResp = getGoalTargets(goal_id)

        return {
            "success": goalTargetResp["success"],
            "data": goalTargetResp["data"],
            "message": goalTargetResp["message"],
        }, 200
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500


@app.route("/api/stream-goal-targets", methods=["GET"])
@cross_origin()
def streamWeekGoals():
    try:
        logging.info("/api/stream-goal-targets GET called")
        goal_id = request.args.get("goal_id")
        return Response(
            stream_with_context(streamGoalTargets(goal_id)),
            content_type="application/json",
        )
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500


@app.route("/api/edit-goals", methods=["PATCH"])
@cross_origin()
def editGoals():
    try:
        logging.info("/api/edit-goals")
        goal_id = request.args.get("goal_id")
        data = request.get_json()
        goalUpdateResponse = editGoalsTargets(goal_id, data)
        return goalUpdateResponse
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500

@app.route("/api/edit-task", methods=["PATCH"])
@cross_origin()
def editTaskStatus():
    try:
        logging.info("/api/edit-goals")
        goal_id = request.json.get("goal_id")
        day_id=request.json.get("day_id")
        task_id=request.json.get("task_id")
        status=request.json.get("status")
        # data = request.get_json()
        goalUpdateResponse = updateTaskStatus(goal_id, day_id, task_id,status)
        return goalUpdateResponse
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500



@app.route("/api/get-dashboard-data/<user_id>", methods=["GET"])
@cross_origin()
def get_dashboard_data(user_id):
    try:
        if not user_id:
            return {"success": False, "message": "user_id is required"}, 400

        # Get progress for user's goals
        user_goals_progress = get_user_goals_progress(user_id)
        if not user_goals_progress.get("success", True):
            return user_goals_progress

        # Get motivational quote
        quote = get_motivational_quote()

        # Combine goals progress and quote into response
        response = {
            "success": True,
            "goals": user_goals_progress.get("goals", []),
            "quote": quote
        }

        return jsonify(response)

    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500