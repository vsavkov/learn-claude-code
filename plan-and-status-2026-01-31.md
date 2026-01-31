# Plan and Status 2026-01-31

Task 1.

1. Read vs0_bash_agent.py
2. Implement function 'chat' in vs0_bash_agent.py
3. Function 'chat' MUST start vs0_bash_agent.py as subprocess
4. The subprocess MUST use the same venv as parent process vs0_bash_agent.py
5. The subprocess MUST
- send a chat query parameter to the model,
- receive a response from the model,
- print the response to the terminal,
- exit
6. After the subprocess exits, the parent process MUST be ready to receive another chat query.

Task 2.

v0_bash_agent.py calls 'subprocess.run' and passes the 'cmd' parameter as string.
Ensure that when python is called as the subprocess,
the venv is activated to ensure a consistent environment.