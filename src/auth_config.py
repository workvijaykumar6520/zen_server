import logging
from db_config import auth_service

logging.basicConfig(level=logging.INFO)
# Retrieve the token from the Authorization header


def decodeAuth(headers):
    auth_header = headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            # Verify the token using Firebase Authentication
            decoded_token = auth_service.verify_id_token(token)
            user_id = decoded_token["uid"]
            logging.info(f"Token verified for user: {user_id}")
            return {"success": True, "data": {user_id}}
        except Exception as e:
            logging.error(f"Token verification failed: {e}")
            return {"success": False, "message": "Invalid or expired token"}, 401
    else:
        return {
            "success": False,
            "message": "Authorization token missing or invalid",
        }, 401
