# utils/llm.py
import logging
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from config import settings
from typing import List, Optional, Dict, Any
import PIL.Image

logger = logging.getLogger(__name__)


class GeminiProvider:
    def __init__(self):
        # We'll configure in each call using settings.gemini_api_key
        pass

    def generate_text(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
    ) -> Any:
        """
        Builds a single prompt from system + messages, then calls Gemini.
        """
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)

        # Build prompt string
        prompt_parts = [f"System: {system_prompt}"]
        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            prompt_parts.append(f"{role}: {content}")

        full_prompt = "\n".join(prompt_parts)

        # Create Gemini model
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": settings.llm_temperature,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )

        # Generate response
        if tools:
            gemini_tools = self._convert_tools(tools)
            response = model.generate_content(
                contents=full_prompt,
                tools=gemini_tools,
            )
        else:
            response = model.generate_content(full_prompt)

        return response

    def generate_vision(self, image_path: str, prompt: str) -> str:
        genai.configure(api_key=settings.gemini_api_key)

        model = genai.GenerativeModel("gemini-2.5-flash")

        img = PIL.Image.open(image_path)
        response = model.generate_content([prompt, img])

        return response.text

    def _convert_tools(self, tools: List[Dict]) -> List[Dict]:
        """Convert tool definitions to Gemini's function_declarations format."""
        function_declarations = []

        for tool in tools:
            function_declarations.append(
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                }
            )

        return [{"function_declarations": function_declarations}]