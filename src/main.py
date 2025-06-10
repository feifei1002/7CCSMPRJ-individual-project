import os
import re

from mistralai import Mistral
from src.code_execution import execute_code_and_tests
from src.config import MISTRAL_API_KEY, PROJECT_DIR, MODEL_NAME
from src.data_utils import load_test_dataset, get_file_extension, load_code_dataset
from src.prompts import CodeTransPrompt


def clean_code(code):
    # Remove triple backticks and language identifiers
    code = code.strip()
    # Remove opening markers like ```java, ```python, etc.
    code = re.sub(r'^```\w+\n', '', code)
    # Remove closing ```
    code = re.sub(r'\n```$', '', code)
    # Remove any standalone ```
    code = code.replace('```', '')
    return code

def main():
    client = Mistral(api_key=MISTRAL_API_KEY)
    source_language = "Java"
    target_language = "Python"

    test_dataset = load_test_dataset(target_language)
    code_dataset = load_code_dataset(source_language)

    output_dir = os.path.join(PROJECT_DIR, f"{source_language.lower()}_to_{target_language.lower()}")
    os.makedirs(output_dir, exist_ok=True)
    results_file = os.path.join(output_dir, "results.txt")

    file_extension = get_file_extension(target_language)
    file_name = "Main.java" if target_language == "Java" else f"main.{file_extension}"
    file_path = os.path.join(output_dir, file_name)

    for index, (code, test) in enumerate(zip(code_dataset, test_dataset)):
        source_code = code.get("canonical_solution")
        declaration = test.get("declaration")
        test_cases = test.get("example_test")

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

        # file_extension = get_file_extension(target_language)
        # file_name = "Main.java" if target_language == "Java" else f"problem_{index}.{file_extension}"
        # file_path = os.path.join(output_dir, file_name)

        with open (file_path, "w") as f:
            cleaned_code = clean_code(translated_code)
            f.write(cleaned_code + "\n")
            f.write(test_cases)

        try:
            result = execute_code_and_tests(file_path, target_language, test_dataset, index)
            compilation_success = result.get("compilation_success", False)
            tests_passed = result.get("tests_passed", False)
            error_message = result.get("error", "")
        except Exception as e:
            compilation_success = False
            tests_passed = False
            error_message = "System error: {str(e)}\n{traceback.format_exc()}"

        with open(results_file, "a") as f:
            f.write(f"Problem {index}:\n")
            f.write(f"Compilation successful: {compilation_success}\n")
            f.write(f"Tests passed: {tests_passed}\n")
            if error_message:
                f.write(f"Error: {error_message}\n")
            f.write("-" * 50 + "\n")
        print(f"Processed problem {index} -> {file_name}")

if __name__ == "__main__":
    main()