from db_config import db


def user_call(data):
    print(data)
    doc_ref = db.collection("users")
    doc_ref.add(data)
    usersStream = doc_ref.stream()
    usersData = []
    for user in usersStream:
        usersData.append(user.to_dict())
    return {"data": usersData, "message": "User created successfully"}
