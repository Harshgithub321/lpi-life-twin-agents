import subprocess
import json
import requests
import sys


def call_lpi_tool(tool_name, args):
    try:
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

        if process.returncode != 0:
            return f"Error calling {tool_name}: {stderr}"

        return stdout.strip()

    except Exception as e:
        return f"Exception in {tool_name}: {str(e)}"


def run_agent(user_input):
    try:
        if not user_input or user_input.strip() == "":
            print("❌ Error: Empty input provided.")
            return

        print("\n🔍 Querying LPI tools...\n")

        # TOOL CALLS (IMPORTANT)
        overview = call_lpi_tool("smile_overview", {})
        insights = call_lpi_tool("get_insights", {"query": user_input})

        print("📊 TOOL OUTPUTS:\n")
        print("SMILE Overview:\n", overview)
        print("\nInsights:\n", insights)

        print("\n🤖 Generating response...\n")

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

        if response.status_code != 200:
            print("❌ API Error:", response.text)
            return

        result = response.json().get("response", "No response generated")

        print("\n✅ FINAL ANSWER:\n")
        print(result)

    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")


if __name__ == "__main__":
    user_input = " ".join(sys.argv[1:])
    run_agent(user_input)
