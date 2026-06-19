import os
from google import genai
from google.genai import types

api_key = "AQ.Ab8RN6IQ3INDuiq1J6oICce3IKNxZFABwFew13ZMCcrJlFsnZQ"
client = genai.Client(api_key=api_key)

try:
    print("Listing available models...")
    for model in client.models.list():
        print(model.name, model.supported_actions)
except Exception as e:
    print("Error listing models:", e)
