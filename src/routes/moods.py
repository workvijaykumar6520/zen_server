import time
from db_config import db
from datetime import datetime, timedelta, timezone
from constants.moodsConstants import moods


def addMoodRecords(data):
    try:
        print(data)
        # // userId, mood, createdAt
        if not (data.get("user_id")) or not (data.get("mood")):
            return {"success": False, "message": "Required fields missing"}

        moodScore = moods.get(data.get("mood"))
        print(moodScore)
        if not data.get("mood") in moods:
            return {"success": False, "message": "Please provide available moods"}
        moodData = {
            "user_id": data.get("user_id"),
            "mood": moodScore,
            "created_at": round(time.time() * 1000),
        }
        doc_ref = db.collection("mood").add(moodData)
        return {"success": True, "message": "Mood created successfully"}
    except Exception as e:
        print("exception occurred while updating:", e)
        return {"success": False, "data": {}, "message": "Failed to add the mood"}


def getMoodsPercentage(user_id):
    try:
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        seven_days_ago_in_ms = int(seven_days_ago.timestamp() * 1000)

        response = (
            db.collection("mood")
            .where("user_id", "==", user_id)
            .where("created_at", ">=", seven_days_ago_in_ms)
            .get()
        )

        mood_records = [doc.to_dict() for doc in response]
        print(mood_records)

        # Extract mood values and convert to integers
        mood_values = [
            int(record["mood"]) for record in mood_records if record["mood"].isdigit()
        ]

        # Calculate the average mood
        if mood_values:
            average_mood = sum(mood_values) / len(mood_values)
        else:
            average_mood = 0

        return {
            "success": True,
            "data": average_mood,
            "message": "Successfully retrieved moods",
        }

    except Exception as e:
        print("exception occurred while updating:", e)
        return {"success": False, "data": {}, "message": "Failed to get the moods"}
