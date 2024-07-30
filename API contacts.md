## /home


## /questionnaire [GET]

You are an experienced Mental health Assistant, you specialize in cognitive sciences and Mental Wellness Assessment

you need to formulate a pre consultation questionnaire to determine the mental state of the patient the questionnaire sections might include the following :-
["Activity Preference", "Goal Preferences", "commitment level"] include any other sections you like 
And you must return a JSON of questionnaire

Example JSON will look something like this :-
```json
{
    "questionnaire": {
        "Mental Wellness Assessment": [
            {
                "question": "How often do you feel anxious ?",
                "options": [
                    "Rarely",
                    "Sometimes",
                    "Often",
                    "Always"
                ],
            }
        ],
        "Activity Preference": [
            {
                "question": "What kind of activities do you like or willing to try ?",
                "options": [
                    "Meditation",
                    "Yoga",
                    "Journaling",
                    "Physical exercise",
                    "Reading self-help books",
                    "Listening to relaxing music",
                    "Creative activities",
                    "Socializing with friends or family",
                    "Other"
                ]
            }
        ]
    }
}
```

## /questionnaire [POST]
post the following response :-
```json
Body :-
{
    "Mental Wellness Assessment": [
        {
            "question": "How often do you feel anxious ?",
            "answer": "rarely"
        }
    ]
}
```

## /goal-recommendation [GET]

need to fetch questionnaire resp from DB

title 
Short Description
Status

long description
benefits


## /goal/:id/tasks [GET]

We need to pass the following to GEMINI to generate 7 days task
title
Short Description

You are an experienced Mental health Assistant, you specialize in cognitive sciences,
Given a patient goal you need to device a 7 days plan to help significantly reduce the patient issue
Here is the patient goal : "anger Management"

You need to give JSON object in the following format
```json
{
    1 : {
        "objective": "Meditate",
        "description": "",
        "tasks": {
            1: {
                "task": "Task 1",
                "status": "",
                "reflection": "" // this is user opinion of the task
            }
        },
    }
}
```

Instructions :-
Here the "objective" is the brief title for the day goal
"description" refers to the description of the objective, why he need to do the tasks
"tasks" : is the list of the tasks the patient might need to do to help resolve the condition


## /goal/:id/tasks [POST]
update or edit the task status of reflection
```json
body:-
{
    "day": {
        "task_id":{
            "task": "Task 1",
            "status": "",
            "reflection": "" // this is user opinion of the task
        },
        "task_id_2":{
            "task": "Task 1",
            "status": "",
            "reflection": "" // this is user opinion of the task
        },
    }
}
```

## mood-insights [GET]

generate content based on user mood (daily mood data)