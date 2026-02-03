from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

from .openai_service import chat_with_thinking, chat_with_web_search


@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
def thinking_test_view(request):
    """
    Test page: submit a prompt, get GPT-5.2 reply (with optional web search).
    Uses OPEN_AI_API_KEY from .env.
    """
    context = {
        "reply": None,
        "reasoning": None,
        "usage": None,
        "error": None,
        "prompt": "",
        "reasoning_effort": "high",
        "use_web_search": False,
        "citations": [],
    }
    if request.method == "POST":
        prompt = (request.POST.get("prompt") or "").strip()
        reasoning_effort = (
            (request.POST.get("reasoning_effort") or "high").strip().lower()
        )
        if reasoning_effort not in ("none", "low", "medium", "high", "xhigh"):
            reasoning_effort = "high"
        use_web_search = request.POST.get("use_web_search") == "on"
        context["prompt"] = prompt
        context["reasoning_effort"] = reasoning_effort
        context["use_web_search"] = use_web_search
        if not prompt:
            context["error"] = "Please enter a prompt."
        else:
            if use_web_search:
                result = chat_with_web_search(prompt, reasoning_effort=reasoning_effort)
                context["reply"] = result.get("reply") or ""
                context["reasoning"] = result.get("reasoning") or ""
                context["citations"] = result.get("citations") or []
            else:
                result = chat_with_thinking(prompt, reasoning_effort=reasoning_effort)
                context["reply"] = result.get("reply") or ""
                context["reasoning"] = result.get("reasoning") or ""
            context["usage"] = result.get("usage")
            context["error"] = result.get("error")
    return render(request, "openai_thinking/thinking_test.html", context)
