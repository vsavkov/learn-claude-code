from anthropic import Anthropic
from dotenv import load_dotenv
import subprocess
import sys
import os

load_dotenv(override=True)

# Initialize Anthropic client (uses ANTHROPIC_API_KEY and ANTHROPIC_BASE_URL env vars)
client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL = os.getenv("MODEL_ID", "claude-sonnet-4-5-20250929")

_SUBPROCESS_FLAG = "VS0_BASH_AGENT_SUBPROCESS"


def _call_model(prompt: str) -> str:
    response = client.messages.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    return "".join(block.text for block in response.content if hasattr(block, "text"))


def chat(prompt: str) -> str:
    if os.getenv(_SUBPROCESS_FLAG) == "1":
        try:
            response_text = _call_model(prompt)
        except Exception as exc:
            response_text = f"Error: {exc}"
        print(response_text)
        return response_text

    env = os.environ.copy()
    env[_SUBPROCESS_FLAG] = "1"
    subprocess.run(
        [sys.executable, os.path.abspath(__file__), prompt],
        env=env,
        cwd=os.getcwd(),
        check=False,
    )
    return ""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Subagent mode: execute task and print result
        # This is how parent agents spawn children via bash
        chat(sys.argv[1])
    else:
        # Interactive REPL mode
        while True:
            try:
                query = input("\033[36m>> \033[0m")  # Cyan prompt
            except (EOFError, KeyboardInterrupt):
                break
            if query in ("q", "exit", ""):
                break
            chat(query)
