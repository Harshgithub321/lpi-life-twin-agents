import subprocess
import json
import requests
import sys

def call_lpi_tool(tool_name, args):
    process = subprocess.Popen(
        ["node", "../lpi-clean/dist/src/index.js"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    request = {
        "tool": tool_name,
        "args": args
    }

    stdout, stderr = process.communicate(json.dumps(request))
    return stdout

def run_agent(user_input):
    print("\n🔍 Querying LPI tools...\n")

    overview = call_lpi_tool("smile_overview", {})
    insights = call_lpi_tool("get_insights", {"query": user_input})

    print("🤖 Generating response...\n")

    prompt = f"""
User Input: {user_input}

SMILE Overview:
{overview}

Insights:
{insights}

Give personalized advice and clearly mention which tools you used.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:1.5b",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()["response"]

    print("\n✅ FINAL ANSWER:\n")
    print(result)

if __name__ == "__main__":
    user_input = " ".join(sys.argv[1:])
    run_agent(user_input)