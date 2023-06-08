import json
import os

import azure.identity
import openai
from flask import Blueprint, Response, current_app, render_template, request, stream_with_context

bp = Blueprint("chat", __name__, template_folder="templates", static_folder="static")

# Configure OpenAI API
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-03-15-preview"
if os.getenv("AZURE_OPENAI_KEY"):
    openai.api_type = "azure"
    openai.api_key = os.getenv("AZURE_OPENAI_KEY")
else:
    openai.api_type = "azure_ad"
    if os.getenv("AZURE_OPENAI_CLIENT_ID"):
        default_credential = azure.identity.ManagedIdentityCredential(client_id=os.getenv("AZURE_OPENAI_CLIENT_ID"))
    else:
        default_credential = azure.identity.DefaultAzureCredential(exclude_shared_token_cache_credential=True)
    token = default_credential.get_token("https://cognitiveservices.azure.com/.default")
    openai.api_key = token.token


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/chat")
def chat_handler():
    # get message from posted JSON
    request_message = request.json["message"]
    response = openai.ChatCompletion.create(
        request_timeout=30,
        engine=os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT", "chatgpt"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant that evaluates JavaScript programming projects according to the rubric and criteria given. You should always follow the rubric."},
            {"role": "user", "content": 
            """
You are evaluating programming projects according to a description and rubric.
Instructions for students:
Project: Fish Tank
This program draws a single fish. Poor lonely fish! For this project, you'll use functions to accompany him with more fish of all different shapes and colors.
1. Create a custom function (like drawFish) that draws a fish. You can build on the starter code or start from scratch.
2. Add at least 2 parameters to the function declaration that control either the position or the size of the fish.
3. Now call that function many times, with different values as arguments, so that your screen is filled with fish.
Student code:
```
background(89, 216, 255);
var centerX = 203;
var centerY = 100;
var bodyLength = 118;
var bodyHeight = 74;
var bodyColor = color(162, 0, 255);
noStroke();
fill(bodyColor);
// body
ellipse(centerX, centerY, bodyLength, bodyHeight);
// tail
var tailWidth = bodyLength/4;
var tailHeight = bodyHeight/2;
triangle(centerX-bodyLength/2, centerY,
         centerX-bodyLength/2-tailWidth, centerY-tailHeight,
         centerX-bodyLength/2-tailWidth, centerY+tailHeight);
// eye
fill(33, 33, 33);
ellipse(centerX+bodyLength/4, centerY, bodyHeight/5, bodyHeight/5);
fill(bodyColor);
// body
ellipse(100, 100, bodyLength, bodyHeight);
// tail
var tailWidth = bodyLength/4;
var tailHeight = bodyHeight/2;
triangle(10, centerY,
         centerX-bodyLength/2-tailWidth, centerY-tailHeight,
         centerX-bodyLength/2-tailWidth, centerY+tailHeight);
// eye
fill(33, 33, 33);
ellipse(centerX+bodyLength/4, centerY, bodyHeight/5, bodyHeight/5);
 
fill(0, 173, 55);
ellipse(74, 406, 10, 200);
ellipse(88, 434, 10, 200);
ellipse(148, 394, 10, 200);
ellipse(114, 424, 10, 200);
ellipse(194, 418, 10, 200);
ellipse(255, 418, 10, 200);
ellipse(177, 429, 10, 200);
ellipse(239, 411, 10, 200);
```

For the code above, fill out the grading rubric below. If all criteria are met (Yes), the project passes evaluation.

*** GRADING RUBRIC ***
This project (does / does not) meet the grading criteria.

(Yes/No): Contains a function that can draw a fish or some other object.
(Yes/No): Must pass in at least two arguments to that function to control position or size.
(Yes/No): Must call that function at least three times or in response to user interaction, to draw multiple objects around the canvas.
(Yes/No): Doesn't have any syntax errors or program logic errors.
            """ 
            },
            {"role": "assistant", "content": """
This project does not meet the grading criteria.

No: Contains a function that can draw a fish or some other object.
No: Must pass in at least two arguments to that function to control position or size.
No: Must call that function at least three times or in response to user interaction, to draw multiple objects around the canvas.
Yes: Doesn't have any syntax errors or program logic errors."""
            },
            {"role": "user", "content": """
You are evaluating programming projects according to a description and rubric.
Instructions for students:
Project: Fish Tank
This program draws a single fish. Poor lonely fish! For this project, you'll use functions to accompany him with more fish of all different shapes and colors.
1. Create a custom function (like drawFish) that draws a fish. You can build on the starter code or start from scratch.
2. Add at least 2 parameters to the function declaration that control either the position or the size of the fish.
3. Now call that function many times, with different values as arguments, so that your screen is filled with fish.
Student code:
```
background(89, 216, 255);
var salad = function(centerX,centerY,bodyLength,bodyColor){
var bodyHeight = bodyLength/2;
noStroke();
fill(bodyColor);
// body
ellipse(centerX, centerY, bodyLength, bodyHeight);
// tail
var tailWidth = bodyLength/4;
var tailHeight = bodyHeight/2;
triangle(centerX-bodyLength/2, centerY,
         centerX-bodyLength/2-tailWidth, centerY-tailHeight,
         centerX-bodyLength/2-tailWidth, centerY+tailHeight);
// eye
fill(33, 33, 33);
ellipse(centerX+bodyLength/4, centerY, bodyHeight/5, bodyHeight/5);
};         
salad(292,311,100, color(201, 191, 84));
salad(169,212,160, color(68, 98, 158));
salad(259,66,77, color(199, 84, 103));
salad(193,249,92, color(168, 62, 122));
salad(116,127,127, color(196, 29, 76));
var PEB=function(E,S){
//ZE PEBBLES
stroke(64, 61, 64);
fill(166, 61, 124);
ellipse(E+5,S+321,S,S);
fill(104, 164, 196);
ellipse(E+70,S+317,S,S);
fill(191, 84, 102);
ellipse(E-41,S+309,S,S);
};
PEB(60,100);
PEB(205,100);
PEB(364,100);
```

For the code above, fill out the grading rubric below. If all criteria are met (Yes), the project passes evaluation.

*** GRADING RUBRIC ***
This project (does / does not) meet the grading criteria.

(Yes/No): Contains a function that can draw a fish or some other object.
(Yes/No): Must pass in at least two arguments to that function to control position or size.
(Yes/No): Must call that function at least three times or in response to user interaction, to draw multiple objects around the canvas.
(Yes/No): Doesn't have any syntax errors or program logic errors.
"""
            },
            {"role": "assistant", "content": """
This project does meet the grading criteria.

Yes: Contains a function that can draw a fish or some other object.
Yes: Must pass in at least two arguments to that function to control position or size.
Yes: Must call that function at least three times or in response to user interaction, to draw multiple objects around the canvas.
Yes: Doesn't have any syntax errors or program logic errors."""
            },
            {"role": "user", "content": """
You are evaluating programming projects according to a description and rubric.
Instructions for students:
Project: Fish Tank
This program draws a single fish. Poor lonely fish! For this project, you'll use functions to accompany him with more fish of all different shapes and colors.
1. Create a custom function (like drawFish) that draws a fish. You can build on the starter code or start from scratch.
2. Add at least 2 parameters to the function declaration that control either the position or the size of the fish.
3. Now call that function many times, with different values as arguments, so that your screen is filled with fish.
Student code:
```
REQUEST_MESSAGE
```

For the code above, fill out the grading rubric below. If all criteria are met (Yes), the project passes evaluation.

*** GRADING RUBRIC ***
This project (does / does not) meet the grading criteria.

(Yes/No): Contains a function that can draw a fish or some other object.
(Yes/No): Must pass in at least two arguments to that function to control position or size.
(Yes/No): Must call that function at least three times or in response to user interaction, to draw multiple objects around the canvas.
(Yes/No): Doesn't have any syntax errors or program logic errors.         
""".replace("REQUEST_MESSAGE", request_message)},
        ],
        stream=False,
    )
    # log the response
    current_app.logger.info(response)
    response_message = response["choices"][0]["message"]["content"]
    return Response(json.dumps({"response": response_message}), mimetype="application/json")
