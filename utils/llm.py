"""
Abstracted LLM interface.
Currently wraps Google Gemini 2.5 Flash (free tier).
"""
import logging
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from config import settings
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

class GeminiProvider:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            "models/gemini-2.5-flash",
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
            generation_config={"temperature": settings.llm_temperature}
        )

    def generate_text(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
    ) -> Any:
        """
        messages: list of dicts with "role" and "content".
        Returns a genai response object (contains .text or .function_call).
        """
        # Combine system prompt and messages into Gemini's flat history format
        chat = self.model.start_chat(history=[])
        # Set system prompt via initial user message? Gemini has no system prompt natively,
        # we'll prepend it to the first user turn.
        # We'll build the full prompt manually:
        prompt_parts = [f"SYSTEM: {system_prompt}\n"]
        for msg in messages:
            if msg["role"] == "user":
                prompt_parts.append(f"USER: {msg['content']}")
            elif msg["role"] == "assistant":
                prompt_parts.append(f"ASSISTANT: {msg['content']}")
            elif msg["role"] == "tool":
                # Tool results we'll include as "FUNCTION RESULT"
                prompt_parts.append(f"FUNCTION RESULT: {msg['content']}")
        prompt = "\n".join(prompt_parts)

        if tools:
            # Convert our tool definitions to Gemini's Tool object
            gemini_tools = self._convert_tools(tools)
            response = self.model.generate_content(
                contents=prompt,
                tools=gemini_tools,
            )
        else:
            response = self.model.generate_content(prompt)

        return response

    def generate_vision(self, image_path: str, prompt: str) -> str:
        """Send an image + text prompt to Gemini Vision."""
        import PIL.Image
        img = PIL.Image.open(image_path)
        response = self.model.generate_content([prompt, img])
        return response.text

    def _convert_tools(self, tools: List[Dict]) -> List:
        """Convert our tool schema to Gemini's Tool format."""
        # Each tool is a dict: {"name": ..., "description": ..., "parameters": ...}
        function_declarations = []
        for tool in tools:
            function_declarations.append({
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            })
        return [{"function_declarations": function_declarations}]