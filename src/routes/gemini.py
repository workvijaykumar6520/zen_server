from routes.utils import gemini_llm


def gemini_call(user_message):
    print(user_message)
    result = gemini_llm.invoke(user_message)
    print("result", result.content)
    return result.content
