Table users {
  id integer [primary key]
  user_id uuid
  username varchar
  password varchar
  email varchar
  profile_picture varchar
  created_at timestamp
  updated_at timestamp
}

Table mood {
  id integer [primary key]
  user_id uuid
  mood json
  created_at timestamp
}

Table daily_assessment {
  id integer [primary key]
  user_id uuid
  created_at timestamp
  updated_at timestamp
}

Table goal {
  id integer [primary key]
  user_id uuid
  goal_name varchar
  goal_status varchar
  goal_plan json // this is the 7 days task json
  /*
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
  */
  created_at timestamp
  updated_at timestamp
}

Table session {
  session_id uuid
  title varchar
  user_id uuid
}

Table chat {
  id integer [primary key]
  chat_from varchar
  session_id uuid
  message varchar
  created_at timestamp
}

Table chat_summary {
  id integer [primary key]
  user_id uuid
  summary varchar
}


// this table will contain the response for questionnaire
Table questionaire {
  id integer [primary key]
  user_id uuid
  questionnaire_resp json
  /*
  {
    "Mental Wellness Assessment": [
      {
        "question": "How often do you feel anxious ?",
        "answer": "rarely"
      }
    ]
  }
  */
  created_at timestamp
}


// Ref: "goal"."user_id" > "users"."user_id"

Ref: "chat"."session_id" < "session"."session_id"

Ref: "users"."user_id" < "session"."user_id"

Ref: "chat_summary"."user_id" < "users"."user_id"

Ref: "mood"."user_id" < "users"."user_id"

Ref: "daily_assessment"."user_id" < "users"."user_id"

Ref: "goal"."user_id" < "users"."user_id"