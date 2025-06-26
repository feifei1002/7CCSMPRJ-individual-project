from anthropic import Anthropic
from google import genai
from mistralai import Mistral
from openai import OpenAI
from google.genai import types

from src.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY


class BaseLLM:
    def generate(self, messages):
        raise NotImplementedError

class MistralLLM(BaseLLM):
    def __init__(self, model_name="mistralai/codestral-2501"):
        self.client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
        self.model_name = model_name

    def generate(self, messages):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=8000,
            temperature=0.0,
            top_p=1.0,
        )
        return response.choices[0].message.content.strip()

class OpenAILLM(BaseLLM):
    def __init__(self, model_name="gpt-4o-mini"):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model_name = model_name

    def generate(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

class ClaudeLLM(BaseLLM):
    def __init__(self, model_name="claude-3-5-haiku-20241022"):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model_name = model_name

    def generate(self, messages):
        # Extract system message from system prompt
        system_message = None
        chat_message = []

        for message in messages:
            if message["role"] == "system":
                system_message = message["content"]
            else:
                chat_message.append({
                    "role": message["role"],
                    "content": message["content"]
                })

        response = self.client.messages.create(
            model=self.model_name,
            system=system_message,
            messages=chat_message,
            max_tokens=8000,
            temperature=0.0,
            top_p=1.0)
        return response.content[0].text.strip()

class GeminiLLM(BaseLLM):
    def __init__(self, model_name="google/gemini-2.5-flash-001"):
        self.client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
        self.model_name = model_name

    def generate(self, messages):
        # Convert messages to the format expected by Gemini
        formatted_content = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            formatted_content += f"{role.upper}: {content}\n"

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=8000,
            temperature=0.0,
            top_p=1.0,

        )
        return response.choices[0].message.content.strip()

class DeepseekLLM(BaseLLM):
    def __init__(self, model_name="deepseek/deepseek-chat-v3-0324"):
        self.client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
        self.model_name = model_name

    def generate(self, messages):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=8000,
            temperature=0.0,
            top_p=1.0,
        )
        return response.choices[0].message.content.strip()