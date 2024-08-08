from db_config import db
import random
import logging
quotes = [
    "The only way to do great work is to love what you do. – Steve Jobs",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill",
    "Believe you can and you're halfway there. – Theodore Roosevelt",
    "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt"
]

def get_motivational_quote():
    # Return a random quote from the list
    return random.choice(quotes)

def get_user_goals_progress(user_id):
    try:
        # Reference to the goals collection with user_id filter
        goals_collection_ref = db.collection('goal')
        goals_query = goals_collection_ref.where('user_id', '==', user_id)
        goals_docs = goals_query.stream()

        all_goals_progress = []

        for goal_doc in goals_docs:
            goal_data = goal_doc.to_dict()
            goal_id = goal_doc.id
            tasks = goal_data.get('goalPlan', {})

            total_tasks = 0
            completed_tasks = 0

            for task_list in tasks.values():
                for task in task_list.get('tasks', {}).values():
                    total_tasks += 1
                    if task.get('status') == 'DONE':
                        completed_tasks += 1

            progress = {
                "goal_id": goal_id,
                "title": goal_data.get('title'),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }

            all_goals_progress.append(progress)

        return {"success": True, "goals": all_goals_progress}

    except Exception as e:
        logging.error(f"Error fetching user goals progress: {e}", exc_info=True)
        return {"success": False, "message": "Internal server error"}, 500