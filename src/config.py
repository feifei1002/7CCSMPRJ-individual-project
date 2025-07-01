import os


OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
PROJECT_DIR = os.getcwd()

LANGUAGE_MAP = {
    "Python": "python",
    "Java": "java",
    "JavaScript": "js",
    "C++": "cpp",
}

FILE_EXTENSION = {
    "Python": "py",
    "Java": "java",
    "JavaScript": "js",
    "C++": "cpp",
}