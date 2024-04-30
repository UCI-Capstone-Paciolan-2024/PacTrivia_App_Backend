# API
## Create a user account
`POST /regDevice`
#### Request
    curl --location '$HOST/regDevice' \
         --header 'Content-Type: application/json' \
         --data '{"deviceID": "d4fd118653914b369a915743093644a5"}'
#### Response
    HTTP/1.1 200 OK
    Server: Werkzeug/3.0.1 Python/3.12.2
    Date: Tue, 30 Apr 2024 02:33:58 GMT
    Content-Type: application/json
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Headers: content-type
    Access-Control-Allow-Methods: GET,OPTIONS,POST
    Content-Length: 70
    Connection: close
     
    {
        'error': None, 
        'data': {
            'token': 'f910431e39fb490ea6274b8628af5177'
        }
    }
Save the token on-device and include it in all other API calls.

## Start a game session
`POST /startSession`
#### Request
    curl --location '$HOST/startSession' \
    --header 'Content-Type: application/json' \
    --data '{
        "token": "d4fd118653914b369a915743093644a5",
        "userLocation":
            ["33.65049375601106, -117.8470197846565"]
    }'
#### Response
 
    HTTP/1.1 200 OK
    Server: Werkzeug/3.0.1 Python/3.12.2
    Date: Tue, 30 Apr 2024 02:46:32 GMT
    Content-Type: application/json
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Headers: content-type
    Access-Control-Allow-Methods: GET,OPTIONS,POST
    Content-Length: 190
    Connection: close
     
    {
        'error': None,
        'data': {
            'game': {
                'id': 0,
                'teams': ['Anteaters', 'Bruins'],
                'start': '2024-04-01T00:00:00', 
                'end': '2024-06-01T00:00:00',
                'max_sessions': 100,
                'questions_per_session': 10
            }
        }
    }

## Start the next question
`POST /getQuestion`
#### Request
    curl --location '$HOST/getQuestion' \
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
    Access-Control-Allow-Headers: content-type
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

## Check and score answer
`POST /checkAnswer`
#### Request
    curl --location '$HOST/checkAnswer' \
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
    Access-Control-Allow-Headers: content-type
    Access-Control-Allow-Methods: GET,OPTIONS,POST
    Content-Length: 
    Connection: close
     
    {
        'error': None,
        'data': {
            'correct': true
            'session_score': 200,
            'question_score': 100,
            'total_score': 0
        }
    }

## Save new sets of questions into the database
`POST /addQuestions`
#### Request
    curl --location '$HOST/addQuestions' \
    --header 'Content-Type: application/json' \
    --data '{
      "secret": "d000d2bad8badbadbadbbadadbadf00d",
      "data": [
        {
          "team": "Anteaters",
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
          "team": "Bruins",
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
    }
#### Response
    HTTP/1.1 200 OK
    Server: Werkzeug/3.0.1 Python/3.12.2
    Date: Tue, 30 Apr 2024 03:11:20 GMT
    Content-Type: application/json
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Headers: content-type
    Access-Control-Allow-Methods: GET,OPTIONS,POST
    Content-Length: 29
    Connection: close
     
    {'error': None, 'data': None}