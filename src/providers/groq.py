import json
from typing import List, Dict, Any

import requests

from src.providers.base import AIProvider


class GroqProvider(AIProvider):
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str, model: str):
        self._api_key = api_key
        self._model = model

    def chat(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048,
        }
        try:
            resp = requests.post(
                self.BASE_URL, headers=headers, json=payload, timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "success": True,
                "content": data["choices"][0]["message"]["content"],
                "model": data.get("model", self._model),
            }
        except requests.exceptions.HTTPError as e:
            body = e.response.text[:500] if e.response is not None else ""
            return {"error": f"HTTP {e.response.status_code}: {body}"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection failed. Check your internet."}
        except requests.exceptions.Timeout:
            return {"error": "Request timed out."}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        except (KeyError, json.JSONDecodeError) as e:
            return {"error": f"Response parse error: {e}"}

    def get_model_name(self) -> str:
        return self._model
