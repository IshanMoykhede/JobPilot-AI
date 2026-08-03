import os
import re

APP_DIR = os.path.join(os.path.dirname(__file__), "app")

IMPORT_PATTERN = re.compile(r'from langchain_google_genai import ChatGoogleGenerativeAI')
INIT_PATTERN = re.compile(r'ChatGoogleGenerativeAI\s*\(')

def migrate_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "ChatGoogleGenerativeAI" not in content:
        return

    # Replace import
    new_content = IMPORT_PATTERN.sub('from app.core.llm_factory import get_llm', content)
    
    # Replace instantiation
    new_content = INIT_PATTERN.sub('get_llm(', new_content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Migrated {filepath}")

def main():
    for root, dirs, files in os.walk(APP_DIR):
        for file in files:
            if file.endswith(".py"):
                migrate_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
