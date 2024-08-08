from constants.constants import mental_health_prompt_template

GET_QUESTIONNAIRE = mental_health_prompt_template + """

you need to formulate a pre consultation questionnaire to determine the mental state of the patient the questionnaire sections might include the following :-
["Activity Preference", "Goal Preferences", "commitment level"] include any other sections you like 
And you must return a JSON of questionnaire

The below is the example json you need to provide as response, Give atleast 10 questions in single sections,

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
"""