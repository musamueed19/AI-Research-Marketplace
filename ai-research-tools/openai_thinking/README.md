# OpenAI GPT-5.2 Extended Thinking Test App

Test app for **GPT-5.2** with **extended thinking** (reasoning) and optional **web search**. Uses `OPEN_AI_API_KEY` from `.env`.

## Features

- **Chat (no web):** GPT-5.2 via Chat Completions with reasoning effort (low → xhigh).
- **Web Search:** GPT-5.2 via Responses API with `web_search` tool — model can search the web for up-to-date info; response includes citations/sources.

## Setup

1. Add to `.env`:

   ```
   OPEN_AI_API_KEY=sk-...
   ```

2. Install dependency (if not already):

   ```bash
   pip install openai
   ```

3. Run server:

   ```bash
   python manage.py runserver
   ```

4. Open: **http://127.0.0.1:8000/openai-thinking/**

## Model

- **Model:** `gpt-5.2`
- **Reasoning effort:** `low`, `medium`, `high`, `xhigh` (extended thinking)

Higher reasoning = more “thinking” before the reply (better for complex questions).
