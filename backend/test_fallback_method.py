from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import os

def main():
    gemini = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key="fake")
    groq = ChatGroq(model="llama3-8b-8192", api_key="fake")
    
    llm = gemini.with_fallbacks([groq])
    try:
        chain = llm.with_structured_output(dict)
        print("Success! RunnableWithFallbacks supports with_structured_output")
    except AttributeError:
        print("AttributeError: RunnableWithFallbacks DOES NOT support with_structured_output")

if __name__ == "__main__":
    main()
