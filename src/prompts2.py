class BasePrompt:
    @staticmethod
    def prompt(context):
        raise NotImplementedError

class InitialPromptWithLLMGeneratedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant that prioritizes test-driven development (TDD). "
        "First generate comprehensive test cases, then translate {source_language} code to {target_language}. "
        "Your primary goal is to translate {source_language} code to {target_language} accurately and passes all test cases. "
        "{test_framework_instructions} "
        "Return both tests and translated code in clearly marked sections using TEST_BEGIN/TEST_END "
        "and CODE_BEGIN/CODE_END markers."
    )
    USER_PROMPT = (
        "Analyze the following {source_language} code to generate thorough test cases in {target_language}: "
        "{source_language} code:\n"
        "\n{code}\n"
        "Using the generated test cases as requirements, translate the {source_language} code to {target_language}. "
        "\n{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Return only the translated code without additional comments or explanations."
    )

    @staticmethod
    def get_test_framework_instructions(target_language):
        if target_language == "Java":
            return (
                "For Java tests, strictly use JUnit 5\n"
                # "- import org.junit.jupiter.api.Test\n"
                # "- import static org.junit.jupiter.api.Assertions.*\n"
                # "- Use @Test annotation (no modifiers)\n"
                # "- Use non-public test methods\n"
                # "- Use modern assertions (assertEquals, assertAll, assertThrows)"
            )
        elif target_language == "Python":
            return (
                "For Python tests, use unittest framework with:\n"
                "- import unittest\n"
                "- class TestSolution(unittest.TestCase)\n"
                "- Use assertEqual, assertTrue, assertRaises methods"
            )
        return ""

    @staticmethod
    def prompt(context):
        test_framework = InitialPromptWithLLMGeneratedTests.get_test_framework_instructions(context["target_language"])
        return [
            {"role": "system", "content": InitialPromptWithLLMGeneratedTests.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"],
                test_framework_instructions=test_framework,
            )},
            {"role": "user", "content": InitialPromptWithLLMGeneratedTests.USER_PROMPT.format(**context)}
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
