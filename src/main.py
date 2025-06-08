import os
from mistralai import Mistral
from src.code_execution import execute_code_and_tests
from src.config import MISTRAL_API_KEY, PROJECT_DIR, MODEL_NAME
from src.data_utils import load_test_dataset, get_file_extension, load_code_dataset
from src.prompts import CodeTransPrompt

def create_file_header(language):
    headers = {
        "Python": "from typing import List\n\n",
        "Java": "import java.util.*;\nimport java.lang.*;\n\npublic class Solution {\n",
        "JavaScript": "// JavaScript Solutions\n\n",
        "C++": "#include <iostream>\n#include <vector>\n#include <string>\nusing namespace std;\n\n",
        "Go": "package main\n\nimport (\n\t\"fmt\"\n)\n\n"
    }
    return headers.get(language, "")

def format_test_case(language, test_case):
    templates = {
        "Python": f"if __name__ == '__main__':\n{test_case}",
        "Java": f"    public static void main(String[] args) {{\n        {test_case}\n    }}\n}}",
        "JavaScript": f"\n{test_case}",
        "C++": f"int main() {{\n    {test_case}\n    return 0;\n}}",
        "Go": f"func main() {{\n\t{test_case}\n}}"
    }
    return templates.get(language, test_case)


def main():
    client = Mistral(api_key=MISTRAL_API_KEY)
    source_language = "Java"
    target_language = "Python"

    test_dataset = load_test_dataset(target_language)
    code_dataset = load_code_dataset(source_language)

    output_dir = os.path.join(PROJECT_DIR, f"{source_language.lower()}_to_{target_language.lower()}")
    os.makedirs(output_dir, exist_ok=True)
    results_file = os.path.join(output_dir, "results.txt")

    for index, (code, test) in enumerate(zip(code_dataset, test_dataset)):
        source_code = code.get("canonical_solution")
        declaration = test.get("declaration")
        test_cases = test.get("test")

        context = {
            "source_language": source_language,
            "target_language": target_language,
            "declaration": declaration,
            "code": source_code,
            "test_cases": test_cases,
            "source_language_lower": source_language.lower(),
            "target_language_lower": target_language.lower(),
        }

        prompt_messages = CodeTransPrompt.prompt(context)
        chat_response = client.chat.complete(model=MODEL_NAME, messages=prompt_messages)
        translated_code = chat_response.choices[0].message.content.strip()

        file_extension = get_file_extension(target_language)
        file_name = f"problem_{index}.{file_extension}"
        file_path = os.path.join(output_dir, file_name)

        with open (file_path, "w") as f:
            f.write(translated_code + "\n")
            f.write(test_cases)

        result = execute_code_and_tests(file_path, target_language, test_dataset, index)

        with open(results_file, "a") as f:
            f.write(f"Problem {index}:\n")
            f.write(f"Compilation successful: {result['compilation_success']}\n")
            f.write(f"Tests passed: {result['tests_passed']}\n")
            f.write("-" * 50 + "\n")
        print(f"Processed problem {index} -> {file_name}")

if __name__ == "__main__":
    main()