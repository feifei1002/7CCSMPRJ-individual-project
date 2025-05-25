import os
import re
import subprocess
from mistralai import Mistral
from datasets import load_dataset


api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)
model = "codestral-mamba-latest"

class CodeTransPrompt:
    system_prompt = (
        "You are an expert in code translation and follow test-driven development (TDD) principles. "
        "Translate the following {source_language} code to {target_language}. Ensure that your translation is executable"
        "and suitable for generating test cases. "
        # "validated by tests. "
    )

    user_prompt = (
        "Here is the {source_language} code:\n"
        "```{source_language_lower}\n{code}\n```\n"
        # "Test Cases:\n"
        # "```{target_language_lower}\n{test_cases}\n```\n\n"
        "Please translate it to {target_language}"
        "The output must be a single Python function with no extra comments or explanation "
        "and make sure to verify it correctness with the test cases."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": CodeTransPrompt.system_prompt.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": CodeTransPrompt.user_prompt.format(
                source_language=context["source_language"],
                target_language=context["target_language"],
                source_language_lower=context["source_language"].lower(),
                target_language_lower=context["target_language"].lower(),
                code=context["code"])},
                # test_cases=context["test_cases"])}
        ]

# Extract the code from the translated response
def extract_python_code(translated_code):
    pattern = r"```python\s*(.*?)\s*```"
    match = re.search(pattern, translated_code, re.DOTALL)
    return match.group(1) if match else None

# Generate Pynguin tests for the extracted Python code
def generate_pynguin_tests(extracted_code, module_name="python_code"):
    project_dir = os.getcwd()
    python_code_path = os.path.join(project_dir, f"{module_name}.py")
    # write the extracted code to a Python file
    with open(python_code_path, "w") as f:
        f.write(extracted_code)

    # execute Pynguin to generate tests
    test_dir = os.path.join(project_dir, "pynguin-report")
    os.makedirs(test_dir, exist_ok=True)
    subprocess.run([
        "pynguin",
        "--project-path", project_dir,
        "--output-path", test_dir,
        "--module-name", module_name,
        "-v"], check=True)

source_language = "Java"
target_language = "Python"


dataset = load_dataset("code_x_glue_cc_code_to_code_trans", "default", split="train[:1]")
for example in dataset:
    java_code = example["java"]
    context = {"source_language": source_language,
                "target_language": target_language,
                "code": java_code}

    prompt_messages = CodeTransPrompt.prompt(context)
    print(prompt_messages)

    chat_response = client.chat.complete(model=model, messages=prompt_messages)
    translated_python_code = chat_response.choices[0].message.content.strip()
    python_code = extract_python_code(translated_python_code)
    generate_pynguin_tests(python_code)