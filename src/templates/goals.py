GET_GOAL_RECOMMENDATION = """
You are an experienced Mental health Assistant, you specialize in cognitive sciences and Mental Wellness Assessment

you need to formulate a pre goal recommendation to help the mental state of the patient :-
The latest questionnaire answered by patient is given below use that and give some best goals that help the patient change the current mood and mental state.

The below is the example json you need to provide as response, Give atleast 5 goals,

{
title 
Short Description
Status

long description
benefits:["benefit1","benefit2","benefit3"]
}

Give the response in array of objects.
Give status as inprogress.
Think like a professional therapist and give the response

Here is the response from patient

"""

GET_GOAL_TARGETS = """
The above is the goal request from the patient.

You are an experienced Mental health Assistant, you specialize in cognitive sciences,
Given a patient goal you need to device a 7 days plan to help significantly reduce the patient issue
Here is the patient goal : "anger Management"

You need to give JSON object in the following format
Example JSON :-
{
    1 : {
        "id": 1
        "objective": "Meditate",
        "description": "",
        "tasks": {
            1: {
                "id": 1
                "task": "Task 1",
                "status": "",
                "reflection": "", // this is user opinion of the task
                "status": "TO_DO"
            }
        },
    },
    2 : {
        "id": 2,
        "objective": "Meditate",
        "description": "",
        "tasks": {
            1: {
                "id": 1
                "task": "Task 1",
                "status": "",
                "reflection": "", // this is user opinion of the task
                "status": "TO_DO"
            }
        },
    }
}

GIVE 7 DAYS GOAL TARGETS AND INCLUDE TO_DO TO EVERY STATUS
Important Note :- Make sure to send proper JSON with proper Escape character, incase " is in the json
"""



MODIFIED_GET_GOAL_TARGETS = """ 
The above is the goal request from the patient.
You are an experienced Mental Health Assistant specializing in cognitive sciences. Given a patient's goal, you need to devise a 7-day plan to help significantly reduce the patient's issue.

You need to provide a JSON object in the following format, giving an incremental ID for each task: {
    1 : {
        "id": 1,
        "objective": "Objective 1",
        "description": "Description of the objective",
        "tasks": {
            1: {
                "id": 1,
                "task": "Task 1 description",
                "status": "In Progress",
                "reflection": "" // This is the user’s opinion of the task
            },
            2: {
                "id": 2,
                "task": "Task 2 description",
                "status": "In Progress",
                "reflection": ""
            }
        }
    },
    2 : {
        "id": 2,
        "objective": "Objective 2",
        "description": "Description of the objective",
        "tasks": {
            1: {
                "id": 3,
                "task": "Task 1 description",
                "status": "In Progress",
                "reflection": "" // This is the user’s opinion of the task
            }
        }
    }
}

Instructions:

For any text inside the JSON that includes double quotes, escape the double quotes by using \" to maintain valid JSON formatting.

Do not use single quotes inside the JSON. If you need to include double quotes within the string values, escape them as follows:

Incorrect: "task": "Practice using "I" statements"

Correct: "task": "Practice using \"I\" statements"

Ensure that each task has an incremental ID, starting from 1 and continuing through all tasks in the 7-day plan.

The status for each task should be "In Progress", and reflection should be an empty string "".

Return the 7 JSON objects as an array in the format provided.
"""