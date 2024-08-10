import time
from db_config import db
from datetime import datetime, timedelta, timezone
from constants.moodsConstants import moods
import os
import google.generativeai as genai
import json
import requests
import concurrent.futures
import logging
from expiringdict import ExpiringDict



def addMoodRecords(data):
    try:
        print(data)
        # // userId, mood, createdAt
        if not (data.get("user_id")) or not (data.get("mood")):
            return {"success": False, "message": "Required fields missing"}

        moodScore = moods.get(data.get("mood"))
        print(moodScore)
        if not data.get("mood") in moods:
            print()
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

        # Extract mood values and calculate the average
        mood_values = [record["mood"] for record in mood_records]

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


# def getYoutubeLinks(query):
#     url = "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q=" + query +"&type=video&key=AIzaSyCNoUN4nPASA9Wfzv9hFv1cpUq3_KtDS2c"

#     payload = {}
#     headers = {}

#     response = requests.request("GET", url, headers=headers, data=payload)

#     return response.text

# def getMoodLinks(mood):
#     try:
#         GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#         genai.configure(api_key=GEMINI_API_KEY)
#         model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

#         prompt = """You are Zen, an experienced Mental Health Assistant with extensive expertise in cognitive sciences and mental wellness. Your primary responsibility is to provide empathetic, non-judgmental support to users seeking guidance on mental health issues.
#                     It has a video reccomendation feature based upon mood.you have to give search terms to search in youtube based upon mood
#                     \n\nMy current mood:""" + mood + """\n\n Provide the array of objects. I want two sections each section contains sectionTitle and searchTerms

#                     Example output: [\{sectionTitle: "",searchTerms:["search term1",...],....\}]
                    
#                     """
#         result = model.generate_content(prompt)
#         text = json.loads(result.text) if result.text else {}
#         finalResult = []
#         for section in text:
#             result = []
#             with concurrent.futures.ThreadPoolExecutor() as executor:
#                 futureQuery = {
#                     executor.submit(getYoutubeLinks, query): query for query in section.get("searchTerms", [])
#                 }
                
#                 for future in concurrent.futures.as_completed(futureQuery):
#                     try:
#                         result.append(json.loads(future.result()))
#                     except Exception as e:
#                         logging.error(f"Exception occurred while processing results for youtube query: {e}")
#             finalResult.append({"sectionTitle": section.get("sectionTitle"), "searchResults": result})

#         return {"success": True, "data": finalResult, "message": "Successfully retrieved mood links"}, 200
#     except Exception as e:
#         print("exception occurred while updating:", e)
#         return {"success": False, "data": {}, "message": "Failed to get the mood links"}, 500






# Initialize the mood cache with a maximum of 100 items and a 24-hour expiration time
mood_cache = ExpiringDict(max_len=100, max_age_seconds=86400)

def get_youtube_links(query):
    """
    Fetch YouTube video links based on a search query.
    """
    url = (
        f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={query}"
        f"&type=video&key=AIzaSyCeDA5742dk5_z7kAeuJraLrWyXiKnNeKY"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Request failed for query '{query}': {e}")
        return {}

def generate_search_terms(mood):
    """
    Generate search terms based on the mood using the Generative AI model.
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

    prompt = (
        f"You are Zen, an experienced Mental Health Assistant with extensive expertise in cognitive sciences and mental wellness. "
        f"Your primary responsibility is to provide empathetic, non-judgmental support to users seeking guidance on mental health issues. "
        f"It has a video recommendation feature based on mood. You have to give search terms to search in YouTube based on mood.\n\n"
        f"My current mood: {mood}\n\nProvide the array of objects. I want two sections, each section containing sectionTitle and searchTerms.\n"
        f"Example output: [{{sectionTitle: '', searchTerms: ['search term1', ...]}}]"
    )

    result = model.generate_content(prompt)
    if not result.text:
        raise ValueError("Failed to generate search terms")
    
    return json.loads(result.text)

def fetch_youtube_links_concurrently(search_terms):
    """
    Fetch YouTube video links concurrently for a list of search terms.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_query = {executor.submit(get_youtube_links, term): term for term in search_terms}
        return [future.result() for future in concurrent.futures.as_completed(future_query)]

def get_mood_links(mood):
    """
    Fetch mood-related YouTube video links, using cache and optimized concurrency.
    """
    try:
        # Check if the mood data is in the cache
        print(mood_cache,"mood_cache")
        if mood in mood_cache:
            return {"success": True, "data": mood_cache[mood], "message": "Successfully retrieved mood links from cache"}, 200

        # Generate search terms based on the mood
        search_data = generate_search_terms(mood)
        final_result = []

        for section in search_data:
            search_terms = section.get("searchTerms", [])
            search_results = fetch_youtube_links_concurrently(search_terms)
            final_result.append({"sectionTitle": section.get("sectionTitle"), "searchResults": search_results})

        # Store the fetched data in the cache
        mood_cache[mood] = final_result

        return {"success": True, "data": final_result, "message": "Successfully retrieved mood links"}, 200

    except Exception as e:
        logging.error(f"Exception occurred while fetching mood links: {e}")
        return {"success": False, "data": {}, "message": "Failed to get the mood links"}, 500