class BasePrompt:
    @staticmethod
    def prompt(context):
        raise NotImplementedError

class InitialPromptWithLLMGeneratedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant that prioritizes test-driven development (TDD). "
        "Your primary goal is to translate {source_language} code to {target_language} accurately and passes all test cases. "
        "Return both tests and translated code in clearly marked sections using TEST_BEGIN/TEST_END "
        "and CODE_BEGIN/CODE_END markers."
    )
    USER_PROMPT = (
        "Translate the following {source_language} test cases to corresponding {target_language}:"
        "{source_language} test cases:\n"
        "\n{test_cases}\n"
        "{test_template}\n"
        "Using the translated test cases as requirements, translate the {source_language} code to {target_language}:\n"
        "{source_language} code:\n"
        "\n{code}\n"
        "\n{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
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
                **context,
                test_template=test_template)}
        ]

class TestFirstPromptWithLLMGeneratedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant that prioritizes test-driven development (TDD). "
        "First generate comprehensive test cases, then translate {source_language} code to {target_language}. "
        "You always start by understanding what the test cases expect before translating the code. "
        "Your primary goal is to translate {source_language} code to {target_language} accurately."
        "You prioritize writing code that passes all provided test cases. "
    )
    USER_PROMPT = (
        "First, analyze the following {source_language} code to generate thorough test cases in {target_language}: "
        "{source_language} code:\n"
        "\n{code}\n"
        "Then, study and understand the generated test cases to determine the expected behavior. "
        "Using the generated test cases as requirements, translate the {source_language} code to {target_language}. "
        "\n{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Return only the translated code without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": TestFirstPromptWithLLMGeneratedTests.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": TestFirstPromptWithLLMGeneratedTests.USER_PROMPT.format(**context)}
        ]

class StepByStepPromptWithLLMGeneratedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant who breaks down complex tasks into manageable steps and prioritizes test-driven development (TDD). "
        "You ensure each step is correct before proceeding to the next."
        "Generate tests first, then translate {source_language} code to {target_language} step by step."
        "Your primary goal is to translate {source_language} code to {target_language} accurately and passes all test cases. "
    )

    USER_PROMPT = (
        "Translate the following {source_language} code to {target_language} using a step-by-step approach:"
        "{source_language} code:\n"
        "\n{code}\n"
        "\n{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Follow these steps:\n"
        "1. Analyze the {source_language} code to generate thorough test cases in {target_language}.\n"
        "2. Analyze the test cases to understand the expected behavior.\n"
        "3. Identify the key components and logic in the {source_language} code.\n"
        "4. Translate each component to their {target_language} equivalents.\n"
        "5. Write the {target_language} translation in the provided section.\n"
        "6. Verify that you translation is executable and passes all test cases.\n"
        "Return only the translated code without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": StepByStepPromptWithLLMGeneratedTests.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": StepByStepPromptWithLLMGeneratedTests.USER_PROMPT.format(**context)}
        ]
