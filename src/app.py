from flask import Flask, request, Response, stream_with_context, jsonify
from flask_cors import cross_origin
import logging
from dotenv import load_dotenv

load_dotenv(".env")
from flask import request
from routes.health import health
from routes.gemini import gemini_call
from routes.users import user_call
from routes.questionnaire import get_questionnaire
from routes.questionnaire import post_questionnaire
from routes.goals import getGoalRecommendation, getGoalTargets

# Note :- THIS FILE SHOULD ONLY CONTAIN ROUTING AND LOGGING

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)


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


@app.route("/api/gemini", methods=["POST"])
@cross_origin()
def _gemini_call_():
    try:
        logging.info("/api/gemini api called")
        data = request.get_json()
        user_message = data.get("message")
        user_id = data.get("user_id")
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
        # questionnaireStatus = get_questionnaire()
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
        response = post_questionnaire(data)
        return {"questionnaire_response": response}, 200
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500


@app.route("/api/goal-recommendation", methods=["GET"])
@cross_origin()
def goalRecommendation():
    try:
        logging.info("/api/goal-recommendation GET called")
        return Response(
            stream_with_context(getGoalRecommendation()),
            content_type="application/json",
        )
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500


@app.route("/api/goal-targets", methods=["GET"])
@cross_origin()
def weekGoals():
    try:
        logging.info("/api/goal-targets GET called")
        data = request.get_json()
        return Response(
            stream_with_context(getGoalTargets(data)),
            content_type="application/json",
        )
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500
