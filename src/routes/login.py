import json
from db_config import db,auth_service


def login_with_google(id_token):
    try:
        # Verify the ID token from the client (Google sign-in token)
        decoded_token = auth_service.verify_id_token(id_token)
        uid = decoded_token['uid']

        # Check if the user already exists in Firestore
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            # Retrieve the user's details and add them to Firestore if they are a new user
            user_info = auth_service.get_user(uid)
            add_user_to_firestore(user_info)
            return {"status": "new_user", "user": user_info.email}
        else:
            # If the user already exists, return the existing user's info
            existing_user_data = user_doc.to_dict()
            return {"status": "existing_user", "user": existing_user_data['email']}
    except auth_service.AuthError as e:
        print(f"Error verifying ID token: {e}")
        return None

def add_user_to_firestore(user_info):
    user_data = {
        'uid': user_info.uid,
        'email': user_info.email,
        'display_name': user_info.display_name,
        'photo_url': user_info.photo_url,
        'created_at': user_info.user_metadata.creation_timestamp,
        'last_login_at': user_info.user_metadata.last_sign_in_timestamp
    }
    db.collection('users').document(user_info.uid).set(user_data)