from transformers import AutoTokenizer

from app.core.config import settings

MODEL_NAME = "meta-llama/Llama-3.1-70B-Instruct"

try:
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        token=settings.HF_TOKEN,
    )

except Exception as e:
    print(f"Failed to load Llama tokenizer: {e}")
    print("Falling back to GPT-2 tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained("gpt2")


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in the given text.
    """
    return len(tokenizer.encode(text))