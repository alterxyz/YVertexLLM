import time
import json

import vertexai

from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Tool,
    grounding,
)

# If you want to use the google build in search for vertexai SDK, you may need to read and pass through serval agreements with Google.
# See <https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/ground-gemini#web-ground-gemini> for more details.
# However, this is just a demo.


# TODO(developer): Update and un-comment below line
project_id = ""  # Fill in your project ID here

vertexai.init(project=project_id, location="us-central1")

model = GenerativeModel("gemini-1.5-flash-001")

# Use Google Search for grounding
tool = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Search Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f0f0f0;
            color: #333;
            transition: background-color 0.3s, color 0.3s;
        }

        h1 {
            color: #333;
            font-size: 2em;
            margin-bottom: 20px;
        }

        .section {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s, box-shadow 0.3s;
        }

        .section h2 {
            color: #444;
            margin-top: 0;
        }

        /* 亮色模式样式 */
        @media (prefers-color-scheme: light) {
            body {
                background-color: #f0f0f0;
                color: #333;
            }

            .section {
                background-color: white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }

            #gemini-response .container {
                background-color: #fafafa !important;
                box-shadow: 0 0 0 1px #0000000f !important;
            }

            #gemini-response .chip {
                background-color: #ffffff !important;
                border-color: #d2d2d2 !important;
                color: #5e5e5e !important;
            }

            #gemini-response .logo-dark {
                display: none !important;
            }

            #gemini-response .logo-light {
                display: inline !important;
            }
        }

        /* 暗色模式样式 */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }

            h1 {
                color: #e0e0e0;
            }

            .section {
                background-color: #2a2a2a;
                box-shadow: 0 2px 4px rgba(255, 255, 255, 0.1);
            }

            .section h2 {
                color: #c0c0c0;
            }

            #gemini-response .container {
                background-color: #2a2a2a !important;
                box-shadow: 0 0 0 1px #ffffff0f !important;
            }

            #gemini-response .chip {
                background-color: #3a3a3a !important;
                border-color: #5a5a5a !important;
                color: #e0e0e0 !important;
            }

            #gemini-response .logo-light {
                display: none !important;
            }

            #gemini-response .logo-dark {
                display: inline !important;
            }
        }
    </style>
</head>

<body>
    <h1>Gemini</h1>
    <div class="section">
        <div class="section">
            <h4>User</h4>
            <p>User_Query</p>
        </div>
        <div class="section">
            <h4>Gemini</h4>
            <p>Response</p>
            <!-- rendered_content -->
        </div>
    </div>
</body>

</html>
"""


def gen_with_web_search_stream(prompt: str):
    """Generates a response using Gemini with web search and saves the interaction to an HTML file.

    Args:
        prompt: The user's prompt for the model.
    """

    responses = model.generate_content(
        prompt,
        tools=[tool],
        generation_config=GenerationConfig(temperature=0.0),
        stream=True,
    )
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    file_name = f"Gemini_{timestamp}.jsonl"
    response_text = ""
    rendered_content = ""

    for response in responses:
        response_dict = response.to_dict()

        if "candidates" in response_dict and response_dict["candidates"]:
            first_key = next(iter(response_dict["candidates"][0]))
            if first_key == "content":
                print(response.text, end="")
                response_text += response.text
            elif first_key == "grounding_metadata":
                # By this way, the rendered content is the original content from Google to maximizily follow their terms of service.
                rendered_content = response_dict["candidates"][0]["grounding_metadata"][
                    "search_entry_point"
                ]["rendered_content"]
            else:
                print(
                    f"\n----\nUnknown candidates Type\nDetails\n{json.dumps(response_dict, indent=2)}\n----"
                )
        elif "usage_metadata" in response_dict:
            continue
        else:
            print(
                f"\n----\nUnknown\nDetails\n{json.dumps(response_dict, indent=2)}\n----"
            )
        with open(file_name, "a") as f:
            f.write(json.dumps(response_dict, ensure_ascii=False) + "\n")

    # Create and save the HTML output
    html_content = HTML_TEMPLATE.replace(
        "<!-- rendered_content -->", f"<p>{rendered_content}</p>"
    )
    html_content = html_content.replace("<p>User_Query</p>", f"<p>{prompt}</p>")
    html_content = html_content.replace(
        "<p>Response</p>", f"<p style='white-space: pre-wrap;'>{response_text}</p>"
    )
    store_html(html_content, timestamp)


def gen_with_web_search(prompt: str):
    """Generates a response using Gemini with web search and saves the interaction to an HTML file.

    Args:
        prompt: The user's prompt for the model.
    """
    response = model.generate_content(
        prompt,
        tools=[tool],
        generation_config=GenerationConfig(temperature=0.0),
    )
    print(response.text)

    response_dict = response.to_dict()
    rendered_content = response_dict["candidates"][0]["grounding_metadata"][
        "search_entry_point"
    ]["rendered_content"]

    # Save the full response as JSON (optional, for debugging)
    save_json_response(response_dict)

    html_content = HTML_TEMPLATE.replace(
        "<!-- rendered_content -->", f"<p>{rendered_content}</p>"
    )
    html_content = html_content.replace("<p>User_Query</p>", f"<p>{prompt}</p>")
    html_content = html_content.replace(
        "<p>Response</p>", f"<p style='white-space: pre-wrap;'>{response.text}</p>"
    )
    store_html(html_content)


def save_json_response(response_dict: dict):
    """Saves the raw JSON response to a file.

    Args:
        response_dict: The dictionary containing the model's response data.
    """

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    file_name = f"Gemini_{timestamp}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(response_dict, f, indent=4, ensure_ascii=False)


def store_html(html_content: str, timestamp: str = None):
    """Saves the HTML content to a file.

    Args:
        html_content: The HTML string to be saved.
    """
    if not timestamp:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
    file_name = f"Gemini_{timestamp}.html"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML file created: {file_name}")


def main(stream: bool = False):
    prompt = input("What you wanna talk with Gemini?\n")
    if stream:
        gen_with_web_search_stream(prompt)
    else:
        gen_with_web_search(prompt)


if __name__ == "__main__":
    main(input("Stream? (True/False/None) "))
