from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
import logging

class DummyPrimary:
    def with_structured_output(self, schema, **kwargs):
        def failing_runnable(prompt):
            raise Exception("Gemini Exhausted!")
        return RunnableLambda(failing_runnable)

class DummyFallback:
    def with_structured_output(self, schema, **kwargs):
        def successful_runnable(prompt):
            return schema(result="Fallback Success!")
        return RunnableLambda(successful_runnable)

class FallbackLLM:
    def __init__(self, primary, fallback):
        self.primary = primary
        self.fallback = fallback

    def with_structured_output(self, schema, **kwargs):
        primary_structured = self.primary.with_structured_output(schema, **kwargs)
        fallback_structured = self.fallback.with_structured_output(schema, **kwargs)
        return primary_structured.with_fallbacks([fallback_structured])

class MySchema(BaseModel):
    result: str

def main():
    llm = FallbackLLM(DummyPrimary(), DummyFallback())
    chain = llm.with_structured_output(MySchema)
    res = chain.invoke("Hello")
    print("Result:", res)

if __name__ == "__main__":
    main()
