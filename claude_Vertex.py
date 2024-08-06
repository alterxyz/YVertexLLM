from datetime import date
from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults
from typing import Any
import os
from anthropic import AnthropicVertex

# TODO(developer): Update and un-comment below line
project_id = ""  # Fill in your project ID here

# Check your gcp account for the region
client = AnthropicVertex(project_id=project_id, region="us-east5")

MODEL_NAME = "claude-3-5-sonnet@20240620"

WOLFRAM_ALPHA_APPID = ""  # Fill in your Wolfram Alpha App ID here
# Go to wolfram alpha and sign up for a developer account here
# <https://developer.wolframalpha.com/>
os.environ["WOLFRAM_ALPHA_APPID"] = WOLFRAM_ALPHA_APPID


def web_search(query: str) -> str:
    search = DuckDuckGoSearchResults()
    return search.run(query)


def wolfram_alpha(query: str) -> str:
    wolfram = WolframAlphaAPIWrapper()
    try:
        result = wolfram.run(query)
    except Exception as e:
        result = f"Wolfram Alpha error: {str(e)}. Try simplifying the question."
    return result


tools = [
    {
        "name": "web_search",
        "description": "Performs a web search with the specified query using DuckDuckGo",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "the query to look up"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "wolfram_alpha",
        "description": "Performs advanced calculations and analysis using Wolfram Alpha",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "the mathematical expression or question to calculate or analyze",
                }
            },
            "required": ["query"],
        },
    },
]


def process_tool_call(tool_name, tool_input):
    if tool_name == "web_search":
        return web_search(tool_input["query"])
    elif tool_name == "wolfram_alpha":
        return wolfram_alpha(tool_input["query"])
    else:
        return f"Unknown tool: {tool_name}"


def tool_use_result(tool_result, messages, tool_use) -> list[dict[str, Any]]:

    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": str(tool_result),
                }
            ],
        },
    )
    return messages


def chat_with_tools_no_actual_tools(message):
    messages = [{"role": "user", "content": message}]

    system_prompt = f"""
    Answer as many questions as you can using your existing knowledge.  
    Only search the web for queries that you can not confidently answer.
    Today's date is {date.today().strftime("%B %d %Y")}
    If you think a user's question involves something in the future that hasn't happened yet, use the search tool.
    """

    response = client.messages.create(
        system=system_prompt,
        model=MODEL_NAME,
        messages=messages,
        max_tokens=1000,
        tool_choice={"type": "auto"},
        tools=tools,
    )
    last_content_block = response.content[-1]
    if last_content_block.type == "text":
        print("Claude did NOT call a tool")
        print(f"Assistant: {last_content_block.text}")
    elif last_content_block.type == "tool_use":
        print("Claude wants to use a tool")
        print(last_content_block)
        # `ToolUseBlock(id='toolu_vrtx_xxxxxxxxxxxxxxxxxx', input={'query': 'Who won the 2024 Miami Grand Prix Formula 1 race'}, name='web_search', type='tool_use')`


def chat(message):
    messages = [{"role": "user", "content": message}]

    system_prompt = f"""
    Answer as many questions as you can using your existing knowledge.  
    Only search the web for queries that you can not confidently answer.
    Today's date is {date.today().strftime("%B %d %Y")}
    If you think a user's question involves something in the future that hasn't happened yet, use the search tool.
    The Wolfram Alpha tool is available for advanced calculations and analysis. If any math expression or question is detected, the tool should be called.
    """

    response = client.messages.create(
        system=system_prompt,
        model=MODEL_NAME,
        messages=messages,
        max_tokens=1000,
        tool_choice={"type": "auto"},
        tools=tools,
    )
    print(f"\n\nResponse: {response.content[0].text}\n\n")
    messages.append({"role": "assistant", "content": response.content})
    if response.stop_reason == "tool_use":
        last_content_block = response.content[-1]
        if last_content_block.type == "tool_use":
            tool_name = last_content_block.name
            tool_inputs = last_content_block.input
            print(f"=======Claude is using {tool_name} Tool=======")
            tool_result = process_tool_call(tool_name, tool_inputs)
            print(
                f"Tool result: {tool_result}\n-------------------\n{messages}\n-------------------\n{last_content_block}\n-------------------\n"
            )
            messages = tool_use_result(tool_result, messages, last_content_block)
            print(f"Merging messages:\n{messages}")
            response = client.messages.create(
                system=system_prompt,
                model=MODEL_NAME,
                messages=messages,
                max_tokens=1000,
                tool_choice={"type": "auto"},
                tools=tools,
            )
            print(f"Response: {response.content[0].text}")

    else:
        print("No tool was called. This shouldn't happen!")


def chat_stream(message: str) -> None:
    messages = [{"role": "user", "content": message}]

    system_prompt = f"""
    Answer as many questions as you can using your existing knowledge.  
    Only search the web for queries that you can not confidently answer.
    Today's date is {date.today().strftime("%B %d %Y")}
    If you think a user's question involves something in the future that hasn't happened yet, use the search tool.
    The Wolfram Alpha tool is available for advanced calculations and analysis. If any math expression or question is detected, the tool should be called.
    """
    with client.messages.stream(
        system=system_prompt,
        model=MODEL_NAME,
        messages=messages,
        max_tokens=4096,
        tool_choice={"type": "auto"},
        tools=tools,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        response = stream.get_final_message()

    messages.append({"role": "assistant", "content": response.content})
    if response.stop_reason == "tool_use":
        last_content_block = response.content[-1]
        if last_content_block.type == "tool_use":
            tool_name = last_content_block.name
            tool_inputs = last_content_block.input
            tool_result = process_tool_call(tool_name, tool_inputs)
            messages = tool_use_result(tool_result, messages, last_content_block)
            with client.messages.stream(
                system=system_prompt,
                model=MODEL_NAME,
                messages=messages,
                max_tokens=4096,
                tool_choice={"type": "auto"},
                tools=tools,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
            response = stream.get_final_message()
            print(f"\n\n\nResponse: {response}")


def main_chat_stream():
    """infinity loop to chat with the assistant"""
    while True:
        query = input("Enter a message: ")
        chat_stream(query)


if __name__ == "__main__":
    test = input(f"Testing tools\nEnter any message for online searching:")
    print(web_search(test))
    print(wolfram_alpha("1+1"))
    # chat(input)
    # chat_stream(input)
    main_chat_stream()
