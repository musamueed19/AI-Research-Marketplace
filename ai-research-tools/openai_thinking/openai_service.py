"""
OpenAI service using GPT-5.2 with extended thinking (reasoning) and optional web search.
Uses OPEN_AI_API_KEY from environment (.env).
"""

import os
from openai import OpenAI


# GPT-5.2 extended thinking: use "high" or "xhigh" for deeper reasoning
DEFAULT_REASONING_EFFORT = "high"


def get_client() -> OpenAI:
    """Build OpenAI client from OPEN_AI_API_KEY in env."""
    api_key = os.getenv("OPEN_AI_API_KEY")
    if not api_key or not api_key.strip():
        raise RuntimeError("Missing OPEN_AI_API_KEY in environment (.env)")
    return OpenAI(api_key=api_key.strip())


def chat_with_thinking(
    prompt: str,
    *,
    model: str = "gpt-5.2",
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    max_tokens: int = 4096,) -> dict:
    """
    Call GPT-5.2 with extended thinking (reasoning_effort: high/xhigh).
    Returns dict with keys: reply, reasoning (if any), usage, error.
    """
    result = {"reply": "", "reasoning": "", "usage": None, "error": None}
    try:
        client = get_client()
        kwargs = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }
        # GPT-5.2 reasoning: none, low, medium, high, xhigh
        if reasoning_effort and reasoning_effort != "none":
            kwargs["reasoning_effort"] = reasoning_effort

        response = client.chat.completions.create(**kwargs)
        choice = response.choices[0] if response.choices else None
        if not choice:
            result["error"] = "Empty response from model"
            return result

        result["reply"] = (choice.message.content or "").strip()
        # Reasoning / chain-of-thought may be in message.reasoning_content (API-dependent)
        if (
            hasattr(choice.message, "reasoning_content")
            and choice.message.reasoning_content
        ):
            result["reasoning"] = (choice.message.reasoning_content or "").strip()
        if response.usage:
            result["usage"] = {
                "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                "total_tokens": getattr(response.usage, "total_tokens", 0),
            }
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


def _parse_responses_output(response) -> tuple[str, list[dict]]:
    """Extract output text and citations from Responses API output items."""
    text_parts = []
    citations = []
    output = getattr(response, "output", None) or []
    for item in output:
        if getattr(item, "type", None) != "message":
            continue
        content = getattr(item, "content", None) or []
        for block in content:
            if getattr(block, "type", None) == "output_text":
                text_parts.append(getattr(block, "text", None) or "")
            annotations = getattr(block, "annotations", None) or []
            for ann in annotations:
                if getattr(ann, "type", None) == "url_citation":
                    citations.append(
                        {
                            "url": getattr(ann, "url", ""),
                            "title": getattr(ann, "title", ""),
                            "start_index": getattr(ann, "start_index", 0),
                            "end_index": getattr(ann, "end_index", 0),
                        }
                    )
    # Fallback: some SDKs expose output_text directly
    if not text_parts and hasattr(response, "output_text"):
        text_parts.append(response.output_text or "")
    return "\n".join(text_parts).strip(), citations


def chat_with_web_search(
    prompt: str,
    *,
    model: str = "gpt-5.2",
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    max_output_tokens: int = 4096,) -> dict:
    """
    Call GPT-5.2 via Responses API with web_search tool (extended thinking + live web).
    Returns dict with keys: reply, reasoning, citations, usage, error.
    """
    result = {
        "reply": "",
        "reasoning": "",
        "citations": [],
        "usage": None,
        "error": None,
    }
    try:
        client = get_client()
        kwargs = {
            "model": model,
            "input": prompt,
            "tools": [{"type": "web_search"}],
            "tool_choice": "auto",
            "max_output_tokens": max_output_tokens,
        }
        if reasoning_effort and reasoning_effort != "none":
            kwargs["reasoning"] = {"effort": reasoning_effort}

        response = client.responses.create(**kwargs)
        result["reply"], result["citations"] = _parse_responses_output(response)
        if not result["reply"]:
            result["error"] = "Empty response from model"
        usage = getattr(response, "usage", None)
        if usage:
            result["usage"] = {
                "prompt_tokens": getattr(usage, "input_tokens", 0)
                or getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "output_tokens", 0)
                or getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
            }
        return result
    except Exception as e:
        result["error"] = str(e)
        return result
