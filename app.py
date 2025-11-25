
---

# Code — `agent.py`
```python
# agent.py
import os
import json
from typing import Dict, Callable, Any, Tuple
from dotenv import load_dotenv
import openai
from rich.console import Console

load_dotenv()
console = Console()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_OPENAI = bool(OPENAI_API_KEY)

if USE_OPENAI:
    openai.api_key = OPENAI_API_KEY

class Tool:
    def __init__(self, name: str, func: Callable[[str], str], description: str):
        self.name = name
        self.func = func
        self.description = description

class SimpleAgent:
    """
    Very small agent that:
    - Uses a language model to parse user intent
    - Decides which tool to run (or answer directly)
    - Returns result
    """

    def __init__(self, tools: Dict[str, Tool], use_openai: bool = USE_OPENAI):
        self.tools = tools
        self.use_openai = use_openai

    def list_tools(self) -> str:
        lines = []
        for t in self.tools.values():
            lines.append(f"- {t.name}: {t.description}")
        return "\n".join(lines)

    def plan(self, prompt: str) -> Tuple[str, str]:
        """
        Ask the LLM (if available) which tool to use and what input.
        Otherwise use a tiny heuristic parser to call tools.
        Returns (action, tool_input) where action is either "answer" or tool name.
        """
        if self.use_openai:
            system = (
                "You are an assistant that chooses the best tool to solve user requests. "
                "Available tools are listed. Reply with a JSON object: {\"action\": <'answer' or tool-name>, "
                "\"input\": <string input for the tool or direct answer> } and nothing else."
            )
            tool_list = self.list_tools()
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": f"Tools:\n{tool_list}\n\nUser request: {prompt}\n"},
            ]
            resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=300)
            text = resp.choices[0].message.content.strip()
            # attempt to parse JSON from response
            try:
                obj = json.loads(text)
                action = obj.get("action", "answer")
                inp = obj.get("input", "")
                return action, inp
            except Exception as e:
                console.log("[yellow]LLM response not JSON, falling back to heuristic[/yellow]")
                # fallback to heuristic below
        # Heuristic simple routing:
        low = prompt.lower()
        if any(x in low for x in ["calculate", "what is", "solve", "+", "-", "*", "/"]):
            return "calculator", prompt
        if any(x in low for x in ["read file", "open file", "cat ", "read "]):
            return "file", prompt.split(" ", 1)[-1] if " " in prompt else ""
        return "answer", prompt

    def run(self, user_prompt: str) -> str:
        action, inp = self.plan(user_prompt)
        if action == "answer":
            # Use LLM (if available) to answer; otherwise echo
            if self.use_openai:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_prompt},
                ]
                resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=300)
                return resp.choices[0].message.content.strip()
            else:
                return f"[MOCK-ANSWER] I would answer: {user_prompt}"
        else:
            tool = self.tools.get(action)
            if not tool:
                return f"Unknown tool: {action}. Available tools: {', '.join(self.tools.keys())}"
            try:
                result = tool.func(inp)
                return f"[TOOL:{tool.name}] {result}"
            except Exception as e:
                return f"[ERROR] tool {tool.name} failed: {e}"
