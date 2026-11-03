"""
NVIDIA Nemotron 3.5 Lightning Integration
Communicates with the NVIDIA NIM API for high-speed, accurate Text-to-SQL generation.
Supports disabling internal thinking for immediate direct SQL generation.
"""

import os
import time
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class NemotronAPIError(Exception):
    """Raised when NVIDIA NIM API returns an error or invalid payload."""
    pass


class NemotronSQLGenerator:
    """NVIDIA Nemotron 3.5 Lightning model client for Text-to-SQL."""

    DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"
    API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 60, max_tokens: int = 512):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.model_id = self.DEFAULT_MODEL

    def is_configured(self) -> bool:
        """Check if NVIDIA API key is configured."""
        return bool(self.api_key and len(self.api_key.strip()) > 8)

    def generate_sql(self, schema_text: str, question: str) -> Dict[str, Any]:
        """
        Generates SQL query for a given schema and natural language question.
        Returns:
            {
                "success": bool,
                "sql": str,
                "raw_response": str,
                "latency_ms": float,
                "token_usage": dict,
                "error": Optional[str]
            }
        """
        if not self.is_configured():
            return {
                "success": False,
                "sql": "",
                "raw_response": "",
                "latency_ms": 0.0,
                "token_usage": {},
                "error": "NVIDIA_API_KEY is not set. Please add NVIDIA_API_KEY to your backend .env file."
            }

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        system_prompt = (
            "You are an expert SQL engineer. Given a database schema and a user question, "
            "generate ONLY an executable SQLite query that answers the question. "
            "Follow these rules strictly:\n"
            "1. Output ONLY the raw SQL query. Do not wrap in markdown quotes, no explanations, no prefix, no thoughts.\n"
            "2. Generate only read-only SELECT or WITH statements.\n"
            "3. Use exact table and column names matching the schema.\n"
            "4. Join tables appropriately using foreign key relationships."
        )

        user_content = f"{schema_text}\n\nQuestion: {question}\n\nSQL Query:"

        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.0,
            "max_tokens": self.max_tokens,
            "stream": False,
            "chat_template_kwargs": {"thinking": False}
        }

        start_time = time.time()
        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            latency_ms = round((time.time() - start_time) * 1000, 2)

            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    return {
                        "success": False,
                        "sql": "",
                        "raw_response": "",
                        "latency_ms": latency_ms,
                        "token_usage": data.get("usage", {}),
                        "error": "API returned an empty choices list."
                    }

                msg = choices[0].get("message", {})
                msg_content = msg.get("content") or msg.get("reasoning_content") or ""
                msg_content = str(msg_content).strip()

                from backend.database.sql_validator import SQLSecurityValidator
                cleaned_sql = SQLSecurityValidator.clean_sql_string(msg_content)

                return {
                    "success": True,
                    "sql": cleaned_sql,
                    "raw_response": msg_content,
                    "latency_ms": latency_ms,
                    "token_usage": data.get("usage", {}),
                    "error": None
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "sql": "",
                    "raw_response": response.text,
                    "latency_ms": latency_ms,
                    "token_usage": {},
                    "error": "Authentication failed: Invalid NVIDIA API key."
                }
            elif response.status_code == 429:
                return {
                    "success": False,
                    "sql": "",
                    "raw_response": response.text,
                    "latency_ms": latency_ms,
                    "token_usage": {},
                    "error": "NVIDIA NIM rate limit exceeded. Please wait a moment and retry."
                }
            else:
                return {
                    "success": False,
                    "sql": "",
                    "raw_response": response.text,
                    "latency_ms": latency_ms,
                    "token_usage": {},
                    "error": f"NVIDIA NIM API error HTTP {response.status_code}: {response.text}"
                }

        except requests.Timeout:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": False,
                "sql": "",
                "raw_response": "",
                "latency_ms": latency_ms,
                "token_usage": {},
                "error": f"NVIDIA NIM API request timed out after {self.timeout}s."
            }
        except Exception as e:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": False,
                "sql": "",
                "raw_response": "",
                "latency_ms": latency_ms,
                "token_usage": {},
                "error": f"Request failed: {str(e)}"
            }
