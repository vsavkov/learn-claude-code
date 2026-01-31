from anthropic import Anthropic
from dotenv import load_dotenv
import subprocess
import sys
import os

load_dotenv(override=True)

# Initialize Anthropic client (uses ANTHROPIC_API_KEY and ANTHROPIC_BASE_URL env vars)
client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL = os.getenv("MODEL_ID", "claude-sonnet-4-5-20250929")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Subagent mode: execute task and print result
        # This is how parent agents spawn children via bash
        print(chat(sys.argv[1]))
    else:
        # Interactive REPL mode
        while True:
            try:
                query = input("\033[36m>> \033[0m")  # Cyan prompt
            except (EOFError, KeyboardInterrupt):
                break
            if query in ("q", "exit", ""):
                break
            print(chat(query))
