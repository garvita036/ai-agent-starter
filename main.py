# main.py
import argparse
from rich.console import Console
from agent import SimpleAgent, Tool
from tools import calculator, file_tool
import os

console = Console()

def build_agent():
    tools = {
        "calculator": Tool("calculator", calculator.run, "Evaluate arithmetic expressions (safe)."),
        "file": Tool("file", file_tool.run, "Read a text file from the project directory (safe)."),
    }
    return SimpleAgent(tools)

def repl(agent):
    console.print("[bold green]AI Agent Starter — Interactive REPL[/bold green]")
    console.print("Type `help` to see tool list, `exit` to quit.\n")
    while True:
        try:
            cmd = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not cmd:
            continue
        if cmd.lower() in ("exit", "quit"):
            break
        if cmd.lower() == "help":
            console.print("Available tools:")
            console.print(agent.list_tools())
            continue
        # pass to agent
        out = agent.run(cmd)
        console.print(f"[cyan]{out}[/cyan]\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo-file", help="Path to demo file to show", default=None)
    args = parser.parse_args()

    if args.demo_file:
        console.print(f"Demo file path: {args.demo_file}")

    agent = build_agent()
    repl(agent)

if __name__ == "__main__":
    main()
