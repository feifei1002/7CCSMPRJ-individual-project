class BasePrompt:
    @staticmethod
    def prompt(context):
        raise NotImplementedError

class InitialPromptWithLLMGeneratedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant focused on test-driven development (TDD). "
        "Your objective is to translate {source_language} code to {target_language} accurately and passes all test cases. "
        "First, translate the test cases to corresponding {target_language} tests. "
        "Then, use those test cases as specifications to translate the code into {target_language}. "
        "Ensure the final translation passes all the generated tests. "
        "Return tests and translated code using TEST_BEGIN/END and CODE_BEGIN/END markers."
    )
    USER_PROMPT = (
        "Translate the following {source_language} test cases to {target_language}:\n\n"
        "{source_language} test cases:\n\n{test_cases}\n"
        "{test_template}\n\n"
        "Then, use the translated test cases as requirements, translate this {source_language} code to {target_language}:\n\n"
        "{source_declaration}\n"
        "\n{code}\n\n"
        "{target_declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Wrap the results as follows:\n"
        "- Enclose test cases with TEST_BEGIN and TEST_END\n"
        "- Enclose the translated code with CODE_BEGIN and CODE_END\n"
        "Return only the translated code without additional comments or explanations."
    )

    @staticmethod
    def get_test_framework_instructions(target_language):
        if target_language == "Java":
            return (
                "Return the translated tests in this structure:\n"
                "TEST_BEGIN\n"
                "import org.junit.jupiter.api.Test;\n"
                "import static org.junit.jupiter.api.Assertions.*;\n\n"
                "public class #CLASS_NAME {\n"
                "    // Your test methods here\n"
                # "    // Each test method should:\n"
                # "    // - Use @Test annotation\n"
                # "    // - Use assertions (assertEquals, assertTrue, etc.)\n"
                "}\n"
                "TEST_END"
            )
        elif target_language == "Python":
            return (
                "Return the translated tests in this structure:\n"
                "TEST_BEGIN\n"
                "import unittest\n"
                "from solution import *\n\n"
                "class TestSolution(unittest.TestCase):\n"
                "    # Your test methods here\n"
                # "    # Each test method should:\n"
                # "    # - Start with 'test_'\n"
                # "    # - Be properly indented (4 spaces)\n"
                # "    # - Use unittest assertions (assertEqual, assertTrue, etc.)\n\n"
                "if __name__ == '__main__':\n"
                "    unittest.main()\n"
                "TEST_END"
            )
        elif target_language == "JavaScript":
            return (
            "Return the translated tests in this structure:\n"
            "TEST_BEGIN\n"
            "const { describe, test, expect } = require('@jest/globals');\n"
            "const solution = require('./solution');\n\n"
            "describe('Solution Tests', () => {\n"
            "    // Your test methods here\n"
            "});\n"
            "TEST_END"
            )
        return ""

    @staticmethod
    def prompt(context):
        test_template = InitialPromptWithLLMGeneratedTests.get_test_framework_instructions(context["target_language"])
        return [
            {"role": "system", "content": InitialPromptWithLLMGeneratedTests.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"],
            )},
            {"role": "user", "content": InitialPromptWithLLMGeneratedTests.USER_PROMPT.format(
                **context, test_template=test_template)}
        ]

class TestFirstPromptWithLLMGeneratedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant focused on test-driven development (TDD). "
        "Your objective is to translate {source_language} code to {target_language} accurately and passes all test cases. "
        "First, translate the test cases to corresponding {target_language} tests. "
        "Then, use those test cases as specifications to translate the code into {target_language}. "
        "You begin by analyzing the test cases to fully understand the required behavior before translating the code. "
        "Ensure the final translation passes all the generated tests. "
        "Return tests and translated code using TEST_BEGIN/END and CODE_BEGIN/END markers."
    )
    USER_PROMPT = (
        "Translate the following {source_language} test cases to {target_language}:\n\n"
        "{source_language} test cases:\n\n{test_cases}\n"
        "{test_template}\n\n"
        "Study and understand the translated test cases to determine the expected behavior. "
        "Then, use the translated test cases as requirements, translate this {source_language} code to {target_language}:\n\n"
        "{source_declaration}\n"
        "\n{code}\n\n"
        "{target_declaration}\n    # INSERT TRANSLATED CODE HERE\n\n"
        "Wrap the results as follows:\n"
        "- Enclose test cases with TEST_BEGIN and TEST_END\n"
        "- Enclose the translated code with CODE_BEGIN and CODE_END\n"
        "Return only the translated code without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        test_template = InitialPromptWithLLMGeneratedTests.get_test_framework_instructions(context["target_language"])
        return [
            {"role": "system", "content": TestFirstPromptWithLLMGeneratedTests.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": TestFirstPromptWithLLMGeneratedTests.USER_PROMPT.format(
                **context, test_template=test_template)}
        ]

class StepByStepPromptWithLLMGeneratedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant who who uses a step-by-step approach and follows test-driven development (TDD). "
        "Your objective is to translate {source_language} code into {target_language} code accurately and passes all provided test cases. "
        "First, translate the test cases to corresponding {target_language} tests. "
        "Then, use those test cases as specifications to translate the code into {target_language}. "
        "You verify each step before proceeding to ensure correctness."
        "Ensure the final translation passes all the generated tests. "
        "Return tests and translated code using TEST_BEGIN/END and CODE_BEGIN/END markers."
    )

    USER_PROMPT = (
        "Translate the following {source_language} test cases to {target_language}:\n\n"
        "{source_language} test cases:\n\n{test_cases}\n"
        "{test_template}\n\n"
        "Then, use the translated test cases as requirements, translate this {source_language} code to {target_language}:\n\n"
        "{source_declaration}\n"
        "\n{code}\n\n"
        "{target_declaration}\n    # INSERT TRANSLATED CODE HERE\n\n"
        "Follow these steps:\n"
        "1. Translate {source_language} test cases to {target_language} test cases \n"
        "2. Analyze the translated test cases to determine the expected behavior.\n"
        "3. Break down the logic of the source code.\n"
        "4. Translate each logical component into {target_language}.\n"
        "5. Combine components into the final function.\n"
        "6. Ensure your translation is syntactically correct and passes all test cases.\n\n"
        "Return only the translated code without additional comments or explanations."
        "Wrap the results as follows:\n"
        "- Enclose test cases with TEST_BEGIN and TEST_END\n"
        "- Enclose the translated code with CODE_BEGIN and CODE_END\n"
        "Return only the translated code without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        test_template = InitialPromptWithLLMGeneratedTests.get_test_framework_instructions(context["target_language"])
        return [
            {"role": "system", "content": StepByStepPromptWithLLMGeneratedTests.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": StepByStepPromptWithLLMGeneratedTests.USER_PROMPT.format(
                **context, test_template=test_template)}
        ]
