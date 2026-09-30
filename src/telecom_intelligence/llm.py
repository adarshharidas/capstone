from __future__ import annotations
 
from typing import Any
 
from .config import Settings
 
 
class GeminiService:
    """Small Gemini adapter with a deterministic fallback for local development."""
 
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Any = None
        if settings.gemini_api_key:
            try:
                from google import genai
 
                self.client = genai.Client(api_key=settings.gemini_api_key)
            except (ImportError, Exception):
                self.client = None
 
    @property
    def available(self) -> bool:
        return self.client is not None
 
    def generate(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("Gemini is not configured; use the local fallback.")
        response = self.client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
        )
        return getattr(response, "text", "").strip()
 
 