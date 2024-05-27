# API
## Create an anonymous user account
`POST /regDevice`
#### Request
    curl --location "$BASE_URL/regDevice" \
         --header 'Content-Type: application/json' \
         --data '{"deviceID": "d4fd118653914b369a915743093644a5"}'
#### Response
    HTTP/1.1 200 OK
    Server: Werkzeug/3.0.1 Python/3.12.2
    Date: Tue, 30 Apr 2024 02:33:58 GMT
    Content-Type: application/json
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Headers: *
    Access-Control-Allow-Methods: GET,OPTIONS,POST
    Content-Length: 70
    Connection: close
     
    {
        'error': None, 
        'data': {
            'token': 'f910431e39fb490ea6274b8628af5177'
        }
    }
Save the token on-device and include it in all other API calls.\
Possible error types:
- InternalError - most likely a bug in the backend

## Start a game session
`POST /startSession`
#### Request
    curl --location "$BASE_URL/startSession" \
    --header 'Content-Type: application/json' \
    --data '{
        "token": "d4fd118653914b369a915743093644a5",
        "userLocation": ["33.65049375601106, -117.8470197846565"],
        "retry": false
    }'

Setting retry to true will repeat the questions from the most recent session and impose a penalty on the subsequent session score.
Otherwise, all questions will be new.

#### Response
 
    HTTP/1.1 200 OK
    Server: Werkzeug/3.0.1 Python/3.12.2
    Date: Tue, 30 Apr 2024 02:46:32 GMT
    Content-Type: application/json
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Headers: *
    Access-Control-Allow-Methods: GET,OPTIONS,POST
    Content-Length: 190
    Connection: close
     
    {
        "error": null,
        "data": {
            "game": {
                "start": "2024-05-22T22:58:32Z",
                "questions_per_session": 10,
                "end": "2024-06-22T22:58:32Z",
                "max_sessions:": -1,
                "teams": [
                    "UC Irvine Anteaters",
                    "UCLA Bruins"
                ],
                "venue_id": "0",
                "team_logos": [
                    "https://upload.wikimedia.org/wikipedia/commons/8/88/UCI_Anteaters_logo.png",
                    "https://upload.wikimedia.org/wikipedia/commons/5/51/Ucla_bruins_bluelogo.png"
                ]
            }
        }
    }

Note: team_logos may contain null values\
Possible error types:
- AuthError - invalid user token
- NoMoreQuestionsError - insufficient number of unique questions in the database for new session (when retry=false)
- NoValidSessionError - could not find a previous session for the nearest active game (when retry=true)
- NoGameFoundError - could not find an active sports game at any of the nearby venues
- InternalError - most likely a bug in the backend

## Start the next question
`POST /getQuestion`
#### Request
    curl --location "$BASE_URL/getQuestion" \
    --header 'Content-Type: application/json' \
    --data '{
        "token": "d4fd118653914b369a915743093644a5",
    }'
#### Response
    HTTP/1.1 200 OK
    Server: Werkzeug/3.0.1 Python/3.12.2
    Date: Tue, 30 Apr 2024 02:23:47 GMT
    Content-Type: application/json
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Headers: *
    Access-Control-Allow-Methods: GET,OPTIONS,POST
    Content-Length: 194
    Connection: close
     
    {
        'error': None,
        'data': {
            'question': 'What is the mascot of the UCI Anteaters?',
            'options': ['Timmy the Tiger',
                        'Harry the Hawk',
                        'Peter the Anteater',
                        'Sammy the Slug'],
            'timeout_seconds': 30
        }
    }

Possible error types:
- AuthError - invalid user token
- NoValidSessionError - user has no active session; either startSession was never invoked, or the underlying game has ended (see game end time in startSession response)
- NoMoreQuestionsError - all questions assigned to the session were already retrieved (refer to 'questions_per_session' in startSession response). Time to start a new session or quit.

## Check and score answer
`POST /checkAnswer`
#### Request
    curl --location "$BASE_URL/checkAnswer" \
    --header 'Content-Type: application/json' \
    --data '{
        "token": "d4fd118653914b369a915743093644a5",
        "answer_index": 2
    }'
#### Response
    HTTP/1.1 200 OK
    Server: Werkzeug/3.0.1 Python/3.12.2
    Date: Tue, 30 Apr 2024 02:25:51 GMT
    Content-Type: application/json
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Headers: *
    Access-Control-Allow-Methods: GET,OPTIONS,POST
    Content-Length: 
    Connection: close
     
    {
        "error": null,
        "data": {
            "subtotal": 170,
            "answer_correct": true,
            "session_finished": false,
            "elapsed_seconds": 9,
            "prev_attempt_count": 0,
            "question_score": 85
        }
    }

Note: total_score is not updated until a new session is started.
Possible error types:
- AnswerTimeoutError - Question timer has expired, an answer was already submitted, or getQuestion was never invoked (frontend should prevent these)
- NoValidSessionError - user has no active session; either startSession was never invoked, or the underlying game has ended (see game end time in startSession response)
- InternalError - most likely a bug in the backend

## Manage questions in database
`POST /questionManager`

Available actions: "add", "list"
#### Request
    curl --location "$BASE_URL/addQuestions" \
    --header 'Content-Type: application/json' \
    --data '{
      "action": "add",
      "secret": "d000d2bad8badbadbadbbadadbadf00d",
      "data": [
        {
          "team": "UC Irvine Anteaters",
          "questions": [
            {
              "question": "In which year was the UCI Anteaters men'\''s basketball team established?",
              "answer_options": ["1970", "1965", "1982", "1991"],
              "correct_indices": [1]
            },
            {
              "question": "Which conference do the UCI Anteaters compete in?",
              "answer_options": ["Big West Conference", "Pac-12 Conference", "Big Ten Conference", "SEC"],
              "correct_indices": [0]
            }
          ]
        },
        {
          "team": "UCLA Bruins",
          "questions": [
            {
              "question": "How many NCAA men'\''s basketball championships have the UCLA Bruins won?",
              "answer_options": ["7", "11", "13", "5"],
              "correct_indices": [1]
            },
            {
              "question": "Which conference do the UCLA Bruins compete in?",
              "answer_options": ["Big West Conference", "Big Ten Conference", "SEC", "Pac-12 Conference"],
              "correct_indices": [3]
            }
          ]
        }
      ]
    }'
#### Response
    {'error': None, 'data': None}


## Manage game events in database
`POST /gameManager`

Available actions: "add", "list"
#### Request
    curl --location "$BASE_URL/addQuestions" \
    --header 'Content-Type: application/json' \
    --data '{
        "action": "add",
        "data": [
            {
                "venue_id": "0",
                "games": [
                    {
                        "start": "2024-05-22T22:58:32Z",
                        "end": "2024-06-22T22:58:32Z",
                        "teams": ["Anteaters", "Bruins"],
                        "max_sessions:": -1,
                        "questions_per_session" : 10
                    }
                ]
            }
        ]
    }'
#### Response
    {'error': None, 'data': None}


# TODO
- nearest venue search using geohash
- venueManager route
- access control for *manager routes
- - 'remove' action for *manager routes
- route to return total user score and global stats