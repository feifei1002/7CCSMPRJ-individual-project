import os
import re

from src.code_execution import execute_code_and_tests
from src.config import PROJECT_DIR
from src.data_utils import load_test_dataset, get_file_extension, load_code_dataset
from src.llms import MistralLLM, ClaudeLLM, GeminiLLM, DeepseekLLM, OpenAILLM
from src.prompts import InitialPrompt, RoleBasedPrompt, TestFirstPrompt, StepByStepPrompt, DirectMappingPrompt


# def clean_code(code):
#     # Remove triple backticks and language identifiers
#     code = code.strip()
#     # Remove opening markers like ```java, ```python, etc.
#     code = re.sub(r'^```\w+\n', '', code)
#     # Remove closing ```
#     code = re.sub(r'\n```$', '', code)
#     # Remove any standalone ```
#     code = code.replace('```', '')
#     return code

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

def main():
    source_language = "Java"
    target_language = "Python"

    llm_models = {
        # "Mistral": MistralLLM(),
        # "OpenAI": OpenAILLM(),
        "Claude": ClaudeLLM(),
        # "Gemini": GeminiLLM(),
        # "DeepSeek": DeepseekLLM()
    }

    prompt_strategies = [
        InitialPrompt,
        RoleBasedPrompt,
        TestFirstPrompt,
        StepByStepPrompt,
        DirectMappingPrompt
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

                # os.remove(file_path)
                print(f"Processed problem {index}")

if __name__ == "__main__":
    main()