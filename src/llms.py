from anthropic import Anthropic
from google import genai
from mistralai import Mistral
from openai import OpenAI

from src.config import MISTRAL_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY


class BaseLLM:
    def generate(self, messages):
        raise NotImplementedError

class CodestralLLM(BaseLLM):
    def __init__(self, model_name="codestral-2501"):
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.model_name = model_name

    def generate(self, messages):
        response = self.client.chat.complete(
            model=self.model_name,
            messages=messages,
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
            max_tokens=8000,
            system=system_message,
            messages=chat_message,)
        return response.content[0].text.strip()

class GeminiLLM(BaseLLM):
    def __init__(self, model_name="gemini-2.0-flash"):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_name = model_name

    def generate(self, messages):
        # Convert messages to the format expected by Gemini
        formatted_content = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            formatted_content += f"{role.upper}: {content}\n"

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=formatted_content,
        )
        return response.text.strip()

class DeepseekLLM(BaseLLM):
    def __init__(self, model_name="deepseek/deepseek-r1-0528:free"):
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://openrouter.ai/api/v1")
        self.model_name = model_name

    def generate(self, messages):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )
        return response.choices[0].message.content.strip()