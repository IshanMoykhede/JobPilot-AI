import asyncio
from pydantic import BaseModel, SecretStr
from app.core.config import settings
from app.core.llm_factory import get_llm

class TestSchema(BaseModel):
    name: str

async def test():
    try:
        llm = get_llm(
            model="gemini-2.0-flash",
            api_key=SecretStr(settings.GEMINI_API_KEY)
        )
        print("Type of LLM:", type(llm))
        structured = llm.with_structured_output(TestSchema)
        print("Success! Type of structured:", type(structured))
    except Exception as e:
        print("Error:", type(e), e)

if __name__ == "__main__":
    asyncio.run(test())
