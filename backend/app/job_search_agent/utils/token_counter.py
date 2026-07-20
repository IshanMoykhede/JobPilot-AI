from transformers import AutoTokenizer
from app.core.config import settings

# Load only once when the application starts
try:
    # Use Llama-3.1 tokenizer as per user request
    tokenizer = AutoTokenizer.from_pretrained(
        "meta-llama/Llama-3.1-70B-Instruct",
        token=settings.HF_TOKEN
    )
except Exception as e:
    print(f"Failed to load Llama tokenizer. Error: {e}")
    # Fallback to gpt2 if HF authentication fails
    tokenizer = AutoTokenizer.from_pretrained("gpt2")

def count_tokens(text: str) -> int:
    """Counts the number of tokens in a text"""
    if tokenizer:
        return len(tokenizer.encode(text))
    # Fallback approximation (1 token ~= 4 chars)
    return len(text) // 4
