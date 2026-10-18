"""
Groq API Client Service.
Provides robust inference with automatic retries, exponential backoff,
JSON mode, model configuration, and graceful demo-mode fallback.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from groq import Groq, APIError, RateLimitError, AuthenticationError
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


# Supported and active Groq models
DEFAULT_GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b"
]


class GroqService:
    """Manages Groq API interactions with retries, backoff, and fallback handling."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        self._client: Optional[Any] = None

        if GROQ_AVAILABLE and self.api_key:
            try:
                self._client = Groq(api_key=self.api_key)
            except Exception:
                self._client = None

    def is_configured(self) -> bool:
        """Returns True if Groq library is present and an API key is provided."""
        return bool(GROQ_AVAILABLE and self.api_key and len(self.api_key.strip()) > 10)

    def test_connection(self) -> Dict[str, Any]:
        """Tests the Groq API key with a minimal call."""
        if not self.is_configured():
            return {
                "success": False,
                "message": "Groq API Key is not configured. Running in Verified Demo Mode."
            }

        try:
            client = Groq(api_key=self.api_key)
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Respond with 'OK'"}],
                max_tokens=5,
                temperature=0.1
            )
            return {"success": True, "message": f"Connection successful! Model: {self.model}"}
        except AuthenticationError:
            return {"success": False, "message": "Invalid Groq API Key. Please verify your credentials."}
        except RateLimitError:
            return {"success": False, "message": "Groq rate limit or quota exceeded. Please check your account."}
        except Exception as e:
            return {"success": False, "message": f"Connection error: {str(e)}"}

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        json_mode: bool = False,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Generates chat completion with exponential backoff for transient errors.
        Never prints or exposes the API key in logs.
        """
        if not self.is_configured():
            return None

        client = Groq(api_key=self.api_key)
        response_format = {"type": "json_object"} if json_mode else None

        for attempt in range(max_retries):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                if response_format:
                    kwargs["response_format"] = response_format

                chat_completion = client.chat.completions.create(**kwargs)
                return chat_completion.choices[0].message.content

            except RateLimitError:
                sleep_time = (2 ** attempt) * 2
                time.sleep(sleep_time)
            except APIError as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Groq API error after {max_retries} retries: {str(e)}")
                time.sleep(2)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Unexpected Groq inference error: {str(e)}")
                time.sleep(2)

        return None
