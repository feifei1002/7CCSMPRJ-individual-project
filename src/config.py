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
    "Go": "go",
}

FILE_EXTENSION = {
    "Python": "py",
    "Java": "java",
    "JavaScript": "js",
    "C++": "cpp",
    "Go": "go",
}

EXECUTION_COMMANDS = {
    "Python": "python3",
    "Java": "java",
    "JavaScript": "node",
    "C++": "g++",
    "Go": "go run",
}

FILE_TEMPLATES = {
    "Java": "{code}\n\n{test_cases}\n}",
    "JavaScript": "{code}\n\n{test_cases}",
    "C++": "#include <iostream>\n{code}\n\n{test_cases}",
    "Go": "package main\n\n{code}\n\n{test_cases}",
    "Python": "{code}\n\n{test_cases}"
}