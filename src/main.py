import os
import re
import traceback

from src.code_execution import execute_code_and_tests
from src.config import PROJECT_DIR
from src.data_utils import load_test_dataset, get_file_extension, load_code_dataset
from src.llms import MistralLLM, ClaudeLLM, GeminiLLM, DeepseekLLM, OpenAILLM
from src.prompts import InitialPromptWithProvidedTests
from src.prompts2 import InitialPromptWithLLMGeneratedTests


def clean_code(code):
    # Extract code between markers only
    code = code.strip()
    marker_match = re.search(r'```(?:\w+)?\n(.*?)\n```', code, re.DOTALL)

    if marker_match:
        # Get only the code within markers
        code = marker_match.group(1).strip()

        # Remove empty lines and trailing whitespace
        code = '\n'.join(line.rstrip() for line in code.splitlines() if line.strip())

        return code

    # If no markers found, return cleaned original code
    return code

def extract_marked_sections(solution_file_path, output_dir):
    """
    Extracts code and test sections from marked blocks in a solution file
    and saves them to separate files.
    """

    with open(solution_file_path, 'r') as f:
        content = f.read()

    # Extract code between CODE_BEGIN/CODE_END
    code_start = content.find('CODE_BEGIN') + len('CODE_BEGIN')
    code_end = content.find('CODE_END')
    code = content[code_start:code_end].strip()

    # Extract tests between TEST_BEGIN/TEST_END
    test_start = content.find('TEST_BEGIN') + len('TEST_BEGIN')
    test_end = content.find('TEST_END')
    tests = content[test_start:test_end].strip()

    # Save code to solution.py
    if code:
        solution_path = os.path.join(output_dir, 'solution.py')
        with open(solution_path, 'w') as f:
            f.write(code)

    # Save tests to test_cases.py
    if tests:
        test_path = os.path.join(output_dir, 'test_cases.py')
        with open(test_path, 'w') as f:
            f.write(tests)

    return bool(code), bool(tests)


def main():
    source_language = "Java"
    target_language = "Python"

    llm_models = {
        # "Mistral": MistralLLM(),
        # "OpenAI": OpenAILLM(),
        # "Claude": ClaudeLLM(),
        # "Gemini": GeminiLLM(),
        "DeepSeek": DeepseekLLM()
    }

    prompt_strategies = [
        InitialPromptWithProvidedTests,
        InitialPromptWithLLMGeneratedTests,
    ]

    test_dataset = load_test_dataset(target_language)
    code_dataset = load_code_dataset(source_language)

    for llm_name, llm in llm_models.items():
        for strategy in prompt_strategies:
            base_folder = f"{source_language.lower()}_to_{target_language.lower()}"
            output_dir = os.path.join(os.path.dirname(PROJECT_DIR), base_folder)
            os.makedirs(output_dir, exist_ok=True)
            results_file = os.path.join(output_dir, f"{strategy.__name__}_{llm_name}.txt")

            file_extension = get_file_extension(target_language)
            temp_file = "Main.java" if target_language == "Java" else f"main.{file_extension}"
            file_path = os.path.join(output_dir, temp_file)

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

                prompt_messages = strategy.prompt(context)
                # chat_response = client.chat.complete(model=MODEL_NAME, messages=prompt_messages)
                # translated_code = chat_response.choices[0].message.content.strip()
                translated_code = llm.generate(prompt_messages)
                cleaned_code = clean_code(translated_code)

                # file_extension = get_file_extension(target_language)
                # file_name = "Main.java" if target_language == "Java" else f"problem_{index}.{file_extension}"
                # file_path = os.path.join(output_dir, file_name)
                if strategy.__module__ == "src.prompts2":
                    with open("solution.py", "w") as f:
                        f.write(cleaned_code)

                    code_found, tests_found = extract_marked_sections('solution.py', output_dir)
                    with open (file_path, "w") as f:
                        if code_found:
                            with open(os.path.join(output_dir, "solution.py"), "r") as code_file:
                                f.write(code_file.read())
                            f.write('\n')
                        if tests_found:
                            with open(os.path.join(output_dir, "test_cases.py"), "r") as test_file:
                                f.write(test_file.read())
                else:
                    with open(file_path, "w") as f:
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

                # os.remove(file_path)
                print(f"Processed problem {index}")

if __name__ == "__main__":
    main()