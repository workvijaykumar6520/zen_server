from db_config import db


def user_call(data):
    print(data)
    doc_ref = db.collection("users")
    doc_ref.add(data)
    return {
      "message": 'User created successfully'
    }
