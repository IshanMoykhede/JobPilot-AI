import os
from langchain_google_genai import ChatGoogleGenerativeAI

api_key = "AQ.Ab8RN6IQ3INDuiq1J6oICce3IKNxZFABwFew13ZMCcrJlFsnZQ"
llm = ChatGoogleGenerativeAI(
    api_key=api_key,
    model="gemini-2.5-flash",
    temperature=0.1
)

try:
    print("Invoking ChatGoogleGenerativeAI...")
    res = llm.invoke("Hello, say 'Gemini 2.5 is working!'")
    print("Response:", res.content)
except Exception as e:
    print("Error:", e)
