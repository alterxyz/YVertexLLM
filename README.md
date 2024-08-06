# Your Vertex AI - LLM cookbook

This would be a good case for:

- Try Vertex AI with Gemini
- Using [Grounding](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview) at Generative AI on Vertex AI
- Practice handling [Function calling](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling) especially tools return
    - Even with **stream** mode
- Claude at Google Cloud Platform - Vertex AI
- Real tool use / function calling with LongChain, DuckDuckGo Search, and Wolfram Alpha

---

## Vertex with Google Search

A CLI based demo, allow you chat with Gemini with the [Grounding with Google Search](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview#ground-public)

### Usage

```bash
python gemini_Vertex.py
```

Then open the generated html file in any browser to see results.

### Setup

Skip to the [Python environment](#python-environment) if you have already setup the gcloud CLI.

#### gcloud CLI init

If you did not install and setup the gcloud, please make sure you download and install, by following the instruction in the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

For initial setup after installing the gcloud, you need to run the following command to authenticate and set the project.

```bash
gcloud init
# then you should login with your browser, choose the project, and set the region
# then you many wanna restart the terminal / Windows system
gcloud info # check if it's correct
```

#### Python environment

```bash
pip install --upgrade google-cloud-aiplatform
gcloud auth application-default login
```

### Note for Gemini

Even with same project (in other llm provider, they may just made it simple as a single string of API key),

there is different from [Google AI Studio](https://aistudio.google.com/app/prompts/new_chat) and [Google Cloud Vertex AI](https://console.cloud.google.com/vertex-ai/generative/multimodal/create/text)

The difference you may see here are:

### Google AI Studio

Support latest gemini mode `model_name="gemini-1.5-pro-exp-0801"`

Support [Code execution](https://ai.google.dev/gemini-api/docs/code-execution?lang=python) which run python NumPy and SymPy,
and it can not install your own libraries,
and it run in google's sandbox so that codes may not safe won't run at your machine.

It's library is `pip install google-generativeai`,

and *All You need is a API key* like other llm providers like openai or claude or cohere.

### Google Cloud Vertex AI

Does not support the latest experimental mode, but has its own exp mode `gemini-experimental` with last update at 7/16/24.

Does not have code execution.

Slighly different code style which require **gcloud** auth and project setup.

---

## Claude with Vertex AI with Tools Use (function calling)

### Claude Usage

```bash
python gemini_Claude.py
```

### Perparation

Make sure you have vaild Google Cloud Platform and granted the permission for Claude at Google Cloud:

<https://console.cloud.google.com/vertex-ai/publishers/anthropic/model-garden/claude-3-5-sonnet>

### Setup_Claude

If you did not install and setup the gcloud, please go [here](#gcloud-cli-init) to install and setup the gcloud.

```bash
pip install --upgrade google-cloud-aiplatform "anthropic[vertex]"
pip install -qU duckduckgo-search langchain-community
pip install wolframalpha
gcloud auth application-default login
```

### Note for Claude and Tools Use

### Tools

For Calculator tool, we picked the Wolfram Alpha as the tool, and for the Search tool, we picked the DuckDuckGo Search API. Those are both easy to get and use.

They are all good services provider, please do not abuse the services.

For Wolfram Alpha, you need to get the App ID from the [Wolfram Alpha](<https://developer.wolframalpha.com/>)

When getting an AppID, it is recommanded to choose the API type as "Short Answers API", since it will return *returns a single plain text result directly from [Wolfram|Alpha](https://products.wolframalpha.com/short-answers-api/documentation)*.

### LongChain

LongChain provides the Python SDK as a wrapper layer for those tools.

### Multi-step Tool Use / Agents

The double call LLM that implement multi-step / auto / infinity tool use is inspired by Cohere's documentation.

While implementing code locally, I use Wolfram Alpha as calculator instead, the preset structure of cohere's calculator was causing some issues.

But it also made great experience that:

I saw the LLM did not get the correct answer as expected, and it try again at least 3 time with self improvement:

First time it added the unit.

Second time it changed the format of the decimal places to natural language instead of quasi-mathematical language.

Third time it adjusted again, because it returned the result but did not yet meet the user's requirements.

I clearlly know it won't happen if there is Prompting with examples (One-, few-, and multi-shot), or Chain of Thought (CoT), or other prompt engineering, or make clear description at tool's defining part.
But if I did remember to do that, I probably won't realize and discover the self-improvement of the LLM.

---

## Ending

I am so appreciated for those organizations and people who provide the great tools and services, and the great documentations and examples.

So I will do that too.

## References

[Ground responses for Gemini models](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/ground-gemini#web-ground-gemini)

[Tool use (function calling) - Anthropic](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)

[Vertex AI API - Anthropic](https://docs.anthropic.com/en/api/claude-on-vertex-ai)

[LongChain DuckDuckGO Search](https://python.langchain.com/v0.2/docs/integrations/tools/ddg/)

[LongChain Wolfram Alpha](https://python.langchain.com/v0.2/docs/integrations/tools/wolfram_alpha/)

[DuckDuckGo Search API](https://duckduckgo.com/api)

[Wolfram|Alpha Short Answers API](https://products.wolframalpha.com/short-answers-api/documentation)

[Multi-step Tool Use (Agents)](https://docs.cohere.com/docs/multi-step-tool-use)

## Additional Notes

Feed back welcome, please open an issue or PR.

This document is almost **fully written by human**,

with a little help **but** just GitHub Copilot and markdown formatting at VSCode.
