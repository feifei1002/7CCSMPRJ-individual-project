import os
import re
import subprocess
from os import mkdir

from mistralai import Mistral
from datasets import load_dataset
#
# ds = load_dataset("openai/openai_humaneval")
#
#
api_key = os.environ["MISTRAL_API_KEY"]
#
client = Mistral(api_key=api_key)
#
model = "codestral-mamba-latest"
#
# prompt = ("Translate this code from Python to Java. "
#           "def convert(minutes): \n return minutes * 60\n")
#
# tests = ("import org.junit.Test;\n"
#          "import static org.junit.Assert.assertEquals;\n"
#          "public class ChallengeTests {\n"
#          "@Test\n"
#          "public void test1() {\n"
#             "assertEquals(360, Challenge.convert(6));\n"
#          "}\n"
#
# 	     "@Test\n"
#          "public void test2() {\n"
#             "assertEquals(240, Challenge.convert(4));\n"
#          "}\n"
#
# 	     "@Test\n"
#          "public void test3() {\n"
#             "assertEquals(480, Challenge.convert(8));\n"
#          "}\n"
#
# 	     "@Test\n"
#          "public void test4() {\n"
#             "assertEquals(3600, Challenge.convert(60));\n"
#          "}\n"
#         "}")
#
# message = [
#     {
#         "role": "system",
#         "content": f"You are a programmer expert in Python and Java, and here is your task: {prompt} "
#                    f"Your code should pass these tests:\n\n{tests}\n"
#     }
# ]
#
# chat_response = client.chat.complete(
#     model=model,
#     messages=message,
# )
# print(chat_response.choices[0].message.content)

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
def extract_python_code(translated_code, module_name="python_code"):
    pattern = r"```python\s*(.*?)\s*```"
    match = re.search(pattern, translated_code, re.DOTALL)
    extracted_code = match.group(1) if match else None
    project_dir = os.getcwd()
    python_code_path = os.path.join(project_dir, f"{module_name}.py")
    print(python_code_path)
    with open(python_code_path, "w") as f:
        f.write(extracted_code)


    test_dir = os.path.join(project_dir, "pynguin-report")
    os.makedirs(test_dir, exist_ok=True)
    subprocess.run([
        "pynguin",
        "--project-path", project_dir,
        "--output-path", test_dir,
        "--module-name", module_name,
        "-v"], check=True)
    # with open(test_file, "w") as tf:
    #     tf.write(pynguin_tests)
    #     return pynguin_tests, extracted_code

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
    extract_python_code(translated_python_code)