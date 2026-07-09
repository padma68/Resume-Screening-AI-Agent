"""
llm_client.py
Thin LLM provider wrapper supporting OpenAI and Groq.

This repo can now use OpenAI or Groq for resume/JD extraction. The
provider is selected with LLM_PROVIDER, and the provider-specific key is
read from OPENAI_API_KEY or GROQ_API_KEY.
"""

import os


def get_completion(system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str:
    """Send a system+user prompt to the configured LLM provider and return text."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        return _openai_completion(system_prompt, user_prompt, max_tokens)
    elif provider == "groq":
        return _groq_completion(system_prompt, user_prompt, max_tokens)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. Use 'openai' or 'groq'."
        )


def _openai_completion(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    from openai import OpenAI

    client = OpenAI()  # reads OPENAI_API_KEY from env
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def _groq_completion(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    import groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER=groq")

    client = groq.Client(api_key=api_key)
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=max_tokens,
        temperature=0.0,
        include_reasoning=False,
        reasoning_effort="low",
        store=False,
    )

    message = response.choices[0].message
    content = getattr(message, "content", None)
    if isinstance(content, str) and content.strip():
        return content
    reasoning = getattr(message, "reasoning", None)
    if isinstance(reasoning, str) and reasoning.strip():
        return reasoning
    # Some Groq responses serialize output into the message object itself.
    return str(message)
