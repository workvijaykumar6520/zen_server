import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, auth


def initializeFirebase():
    cred = credentials.Certificate("zenapp-39c88-74bc5d2e3f1b.json")
    app = firebase_admin.initialize_app(cred)
    db = firestore.client(app)
    auth_service = auth
    return db, auth_service

db, auth_service = initializeFirebase()

