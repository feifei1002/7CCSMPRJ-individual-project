class BasePrompt:
    @staticmethod
    def prompt(context):
        raise NotImplementedError

class NoTestPrompt(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant that prioritize test-driven development (TDD). "
        "Your primary goal is to translate {source_language} code to {target_language} accurately."
    )
    USER_PROMPT = (
        "Translate the following {source_language} code to {target_language} while ensuring it passes the provided test cases. "
        "{source_language} code:\n"
        "\n{code}\n"
        "{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Return only the translated code without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": NoTestPrompt.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": NoTestPrompt.USER_PROMPT.format(**context)}
        ]

class InitialPromptWithProvidedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant that prioritizes test-driven development (TDD). "
        "Your primary goal is to translate {source_language} code to {target_language} accurately and passes all provided test cases. "

    )
    USER_PROMPT = (
        "Translate the following {source_language} code to {target_language} while ensuring it passes the provided test cases. "
        "{source_language} code:\n"
        "\n{code}\n"
        "{target_language} test cases:\n"
        "\n{test_cases}\n"
        "\n{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Return only the translated code without additional comments or explanations."
        # "Return only the full {target_language} code with no extra comments, explanation and markers."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": InitialPromptWithProvidedTests.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": InitialPromptWithProvidedTests.USER_PROMPT.format(**context)}
        ]

class TestFirstPromptWithProvidedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant that prioritizes test-driven development (TDD). "
        "You always start by understanding what the test cases expect before translating the code. "
        "Your primary goal is to translate {source_language} code to {target_language} accurately."
        "You prioritize writing code that passes all provided test cases. "
    )
    USER_PROMPT = (
        "These {target_language} test cases define the required behavior: "
        "{test_cases}\n"
        "Based on these test requirements, translate this {source_language} code to {target_language}: "
        "{source_language} code:\n"
        "\n{code}\n"
        "\n{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Return only the translated code without additional comments or explanations.")

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": TestFirstPromptWithProvidedTests.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": TestFirstPromptWithProvidedTests.USER_PROMPT.format(**context)}
        ]

class StepByStepPromptWithProvidedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant who breaks down complex tasks into manageable steps and prioritizes test-driven development (TDD). "
        "You ensure each step is correct before proceeding to the next."
        "Your primary goal is to translate {source_language} code to {target_language} accurately and passes all provided test cases. "
    )

    USER_PROMPT = (
        "Translate the following {source_language} code to {target_language} using a step-by-step approach:"
        "{source_language} code:\n"
        "\n{code}\n"
        "{target_language} test cases:\n"
        "\n{test_cases}\n"
        "\n{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Follow these steps:\n"
        "1. Analyze the test cases to understand the expected behavior.\n"
        "2. Identify the key components and logic in the {source_language} code.\n"
        "3. Translate each component to their {target_language} equivalents.\n"
        "4. Write the {target_language} translation in the provided section.\n"
        "5. Verify that you translation is executable and passes all test cases.\n"
        "Return only the translated code without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": StepByStepPromptWithProvidedTests.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": StepByStepPromptWithProvidedTests.USER_PROMPT.format(**context)}
        ]