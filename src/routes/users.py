from db_config import db


def user_call(data):
    print(data)
    doc_ref = db.collection("users").document("1")
    doc_ref.set({"firstName": "satyanarayana", "last": "Raju", "born": 2001})
