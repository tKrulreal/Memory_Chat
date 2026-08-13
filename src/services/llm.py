import json
import os
import re
from datetime import datetime
from typing import Any

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import get_settings


class LLMGateway:
    def __init__(self):
        self.settings = get_settings()
        self.chat_model = ChatOpenAI(
            model=self.settings.model_name,
            api_key=self.settings.openai_api_key,
            temperature=self.settings.llm_temperature,
            request_timeout=30.0
        )
        self.embed_model = OpenAIEmbeddings(
            model=self.settings.embedding_model,
            api_key=self.settings.openai_api_key
        )
        self.log_dir = ".ai-log"
        os.makedirs(self.log_dir, exist_ok=True)

    def _log_interaction(self, method: str, prompt: Any, response: Any, kwargs: dict):
        if self.settings.app_env != "development":
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

        log_file = os.path.join(self.log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.jsonl")
        log_entry = {
            "ts": datetime.now().isoformat(),
            "method": method,
            "prompt": mask_pii(prompt),
            "response": mask_pii(response),
            "kwargs": mask_pii(kwargs)
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, prompt: str, **kwargs) -> str:
        try:
            resp = self.chat_model.invoke(prompt, **kwargs)
            result = resp.content
            self._log_interaction("complete", prompt, result, kwargs)
            return result
        except Exception as e:
            self._log_interaction("complete_error", prompt, str(e), kwargs)
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def chat(self, messages: list[BaseMessage], **kwargs) -> str:
        try:
            resp = self.chat_model.invoke(messages, **kwargs)
            result = resp.content
            # Convert messages to strings for safe JSON serialization
            safe_messages = [str(m) if not hasattr(m, 'content') else m.content for m in messages]
            self._log_interaction("chat", safe_messages, result, kwargs)
            return result
        except Exception as e:
            safe_messages = [str(m) if not hasattr(m, 'content') else m.content for m in messages]
            self._log_interaction("chat_error", safe_messages, str(e), kwargs)
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def embed(self, text: str) -> list[float]:
        try:
            result = self.embed_model.embed_query(text)
            self._log_interaction("embed", text, "Vector generated", {})
            return result
        except Exception as e:
            self._log_interaction("embed_error", text, str(e), {})
            raise e

# Maintain backwards compatibility
def get_llm() -> ChatOpenAI:
    return LLMGateway().chat_model
