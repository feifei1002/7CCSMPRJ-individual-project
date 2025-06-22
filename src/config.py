import os


OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
PROJECT_DIR = os.getcwd()

LANGUAGE_MAP = {
    "Python": "python",
    "Java": "java",
}

FILE_EXTENSION = {
    "Python": "py",
    "Java": "java",
}

class LLMConfig:
    UNIFIED_MODEL = "unified"  # Use same model for all prompts
    SPLIT_MODEL = "split"  # Use different models for different prompts

    # Default configurations
    MODE = UNIFIED_MODEL
    DEFAULT_MODEL = "deepseek"
    TEST_MODEL = "codestral"
    TRANSLATION_MODEL = "deepseek"