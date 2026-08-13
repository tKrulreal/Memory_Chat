import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential

VN_TZ = timezone(timedelta(hours=7))


class LLMGateway:
    def __init__(
        self,
        model_name: str | None = None,
        temperature: float = 0.7,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        """
        Initialize LLM Gateway with flexible provider support.

        Supports:
        - OpenAI (default)
        - OpenRouter (https://openrouter.ai)
        - Other OpenAI-compatible APIs

        Args:
            model_name: Model to use (default: gpt-4o-mini)
            temperature: Sampling temperature (default: 0.7)
            api_key: API key (falls back to environment)
            base_url: Custom API base URL (for OpenRouter or proxies)
        """
        from src.config import get_settings
        settings = get_settings()

        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))
        self.temperature = temperature
        self.log_dir = os.getenv("AI_LOG_DIR", ".ai-log")

        # Determine provider
        use_openrouter = os.getenv("USE_OPENROUTER", "false").lower() == "true"
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

        if use_openrouter and openrouter_key:
            # OpenRouter configuration
            self.base_url = "https://openrouter.ai/api/v1"
            self.api_key = openrouter_key
            self.model_name = model_name or os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku")
            self.provider = "openrouter"
        elif base_url:
            # Custom base URL
            self.base_url = base_url
            self.api_key = api_key or settings.openai_api_key
            self.model_name = model_name or "gpt-4o-mini"
            self.provider = "custom"
        else:
            # Default OpenAI
            self.base_url = None
            self.api_key = api_key or settings.openai_api_key
            self.model_name = model_name or "gpt-4o-mini"
            self.provider = "openai"

        # Initialize LLM
        llm_kwargs = {
            "model": self.model_name,
            "temperature": self.temperature,
            "request_timeout": self.timeout,
            "api_key": self.api_key,
        }
        if self.base_url:
            llm_kwargs["base_url"] = self.base_url

        self.llm = ChatOpenAI(**llm_kwargs)

        # Initialize embeddings (use OpenAI for now, can be extended)
        embed_kwargs = {"api_key": self.api_key}
        if self.base_url and self.provider == "openrouter":
            embed_kwargs["base_url"] = "https://openai.com/v1"  # OpenRouter doesn't support embeddings well
        self.embed_model = OpenAIEmbeddings(**embed_kwargs)

        os.makedirs(self.log_dir, exist_ok=True)

    def _log_interaction(self, prompt: str, response: str, method: str):
        if os.getenv("APP_ENV", "development") != "development":
            return

        def mask_pii(data: Any) -> Any:
            if isinstance(data, dict):
                return {k: mask_pii(v) for k, v in data.items()}
            elif isinstance(data, (list, tuple)):
                return type(data)(mask_pii(v) for v in data)
            elif isinstance(data, str):
                try:
                    parsed = json.loads(data)
                    if isinstance(parsed, (dict, list)):
                        return json.dumps(mask_pii(parsed), ensure_ascii=False)
                except Exception:
                    pass

                text = data
                text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL MASKED]', text)
                text = re.sub(r'(?i)(password|secret|key|token)["\'\s:=]+[^\s,\]}]+', r'\1: [REDACTED]', text)
                return text
            return data

        date_str = datetime.now(VN_TZ).strftime('%Y-%m-%d')
        log_file = os.path.join(self.log_dir, f"{date_str}.jsonl")

        entry = {
            "ts": datetime.now(VN_TZ).isoformat(),
            "tool": "llm-gateway",
            "event": "LLM_Request",
            "entry_id": f"gateway-{datetime.now(VN_TZ).strftime('%Y%m%d-%H%M%S')}",
            "model": self.model_name,
            "method": method,
            "prompt": mask_pii(prompt),
            "response": mask_pii(response)
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, prompt: str) -> str:
        """Simple text completion"""
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        result = str(response.content)
        self._log_interaction(prompt=prompt, response=result, method="complete")
        return result

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Chat completion with system instructions"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.llm.invoke(messages)
        result = str(response.content)
        self._log_interaction(
            prompt=f"SYS: {system_prompt}\nUSER: {user_prompt}",
            response=result,
            method="chat"
        )
        return result

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def embed(self, text: str) -> list[float]:
        """Generate embeddings"""
        result = self.embed_model.embed_query(text)
        self._log_interaction(prompt=text, response=f"Vector dimension: {len(result)}", method="embed")
        return result
