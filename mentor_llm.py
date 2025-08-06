import requests
from config import VULTR_API_KEY, VULTR_API_BASE, VULTR_MODEL

class MentorLLM:
    """
    Robust LLM client for Dexter using Vultr Inference API.
    - Uses chat completions endpoint.
    - Supports system prompt, context/history, and config.
    - Returns a string, always, with user-friendly error if anything fails.
    """

    def __init__(self, api_key=None, api_base=None, model=None):
        self.api_key = api_key or VULTR_API_KEY
        self.api_base = api_base or VULTR_API_BASE
        self.model = model or VULTR_MODEL

    def respond(self, prompt, context=None, system=None, max_tokens=50000, temperature=0.5):
        """
        Unified call for DexterBrain: sends context, system prompt, and user prompt.
        """
        return self.ask(prompt, context=context, system=system, max_tokens=max_tokens, temperature=temperature)

    def ask(self, prompt, context=None, system=None, max_tokens=800000, temperature=0.5):
        """
        Sends a prompt to Vultr Inference chat API (OpenAI compatible).
        Supports optional context and system message.
        """
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        # Add multi-turn context (if provided as chat list)
        if context and isinstance(context, list):
            for chat in context:
                # Should be {'role': 'user'/'dexter'/'assistant', 'msg': '...'}
                role = chat.get("role", "user")
                # Normalize 'dexter' to 'assistant' for OpenAI schema
                if role == "dexter":
                    role = "assistant"
                messages.append({"role": role, "content": chat.get("msg", "")})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            resp = requests.post(url, headers=headers, json=data, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            # Vultr returns OpenAI-style response
            content = result["choices"][0]["message"]["content"]
            return content.strip()
        except Exception as e:
            # Graceful error for Dexter
            return f"[MentorLLM error: {e}]"

