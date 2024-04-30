#imported necessaey libraries flask for web application functionality
from flask import Flask, request, jsonify
from flask_cors import CORS

#Access environment variables
import os

import openai
from openai import OpenAI

#logging errors and information.
import logging


#Create new Flask application instance
app = Flask(__name__)


# Basic logging
logging.basicConfig(level=logging.INFO)

#DStored in environment varaible
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    app.logger.error("API Key not found. Please check your environment variables.")
    exit()
else:
    app.logger.error("API Key found.")

#Initialises the OpenAI client which is used to send requests to OpenAI
if openai_api_key:
    client = openai.OpenAI(api_key=openai_api_key)

#A route that returns a welcome message
@app.route('/')
def welcome():
    return 'Welcome to the Flask application! Use the /generate_z3_code endpoint with a POST request to generate Z3 code.'

# Function constructs a prompt using the categories and constraints provided by the user.
def query_chatgpt(categories, constraints, model="gpt-4", max_tokens=500):
    prompt = """
Please generate Python code using the Z3 solver library to solve a logic puzzle based on the given details. 
The solution should model entities and their relationships and enforce constraints strictly to find a unique solution. 
The code should:

    1. Define variables for each entity involved.
    2. Apply given constraints to these variables to model the puzzle accurately.
    3. Ensure that each entity is uniquely assigned and respects all puzzle conditions.
    4. Solve the puzzle and print the solution in a readable format, showing the relationships between entities.

Details are as follows:
- Categories: {}
- Constraints: {}
    """.strip().format(categories, constraints)
    
#sends this prompt to the OpenAI API, requesting a completion that generates Python code using the Z3 solver library.
    try:
        chat_completion = client.chat.completions.create(
            model=model,
             messages=[
                
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.5,
            top_p=1.0,
            n=1,
            stop=None
        )
        return chat_completion
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return {"error": f"An error occurred: {e}"}

#The endpoint(/generate_z3_code) listens for POST requests and expects json data containing categories and constrainst which is then passes through the function above.
@app.route('/generate_z3_code', methods=['POST'])
def generate_z3_code():
    data = request.json
    categories = data.get('categories', '')
    constraints = data.get('constraints', '')

    #Calls query_chatgpt with these details to generate Z3 solver code.
    response = query_chatgpt(categories, constraints, model="gpt-4", max_tokens=500)
    if response:
        try:
            generated_content = response.choices[0].message.content
            print(generated_content)

            # Formatting the generated content
            if "```python" in generated_content:
                formatted_code = generated_content.rstrip("\n")
            else:
                formatted_code = "```python\n" + generated_content + "\n```"
            
            # Return the possibly formatted code in the response
            return jsonify({"z3_code": formatted_code})
        except Exception as e:
            return jsonify({"error": f"Failed to access generated content: {e}"}), 500
    else:
        return jsonify({"error": "Failed to obtain response."}), 500















