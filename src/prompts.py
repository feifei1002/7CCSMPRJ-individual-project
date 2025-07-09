class BasePrompt:
    @staticmethod
    def prompt(context):
        raise NotImplementedError

class NoTestPrompt(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant focused on test-driven development (TDD). "
        "Your objective is to translate {source_language} code to {target_language} accurately."
    )
    USER_PROMPT = (
        "Translate the following {source_language} code to {target_language}.\n\n "
        "{source_language} code:"
        "{source_declaration}\n"
        "\n{code}\n\n"
        "{target_declaration}\n    # INSERT TRANSLATED CODE HERE\n\n"
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

class BasicPromptWithProvidedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant focused on test-driven development (TDD). "
        "Your objective is to translate {source_language} code into {target_language} accurately and passes all provided test cases. "

    )
    USER_PROMPT = (
        "Translate the following {source_language} code to {target_language}, ensuring it passes the provided test cases.\n\n"
        "{source_language} code:"
        "{source_declaration}\n"
        "\n{code}\n\n"
        "{target_language} test cases:\n\n{test_cases}\n\n"
        "{target_declaration}\n   # METHOD BODY OF TRANSLATED CODE WOULD BE HERE\n"
        "Return only the translated code without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": BasicPromptWithProvidedTests.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": BasicPromptWithProvidedTests.USER_PROMPT.format(**context)}
        ]

class TestFirstPromptWithProvidedTests(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant focused on test-driven development (TDD). "
        "You begin by analyzing the test cases to fully understand the required behavior before translating the code. "
        "Your objective is to translate {source_language} code into {target_language} code accurately and passes all provided test cases. "
    )
    USER_PROMPT = (
        "Start by understanding these {target_language} test cases:\n\n{test_cases}\n\n"
        "Now, based on this expected behavior, translate this following {source_language} code to {target_language}:\n\n"
        "{source_language} code:"
        "{source_declaration}\n"
        "\n{code}\n\n"
        "{target_declaration}\n    # INSERT TRANSLATED CODE HERE\n"
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
        "You are a code translation assistant who uses a step-by-step approach and follows test-driven development (TDD). "
        "Your objective is to translate {source_language} code into {target_language} code accurately and passes all provided test cases. "
        "You verify each step before proceeding to ensure correctness."
    )

    USER_PROMPT = (
        "Translate the following {source_language} code to {target_language} using a step-by-step approach:\n\n"
        "{source_language} code:"
        "{source_declaration}\n"
        "\n{code}\n\n"
        "{target_language} test cases:\n\n{test_cases}\n"
        "{target_declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Follow these steps:\n"
        "1. Analyze the test cases to determine the expected behavior.\n"
        "2. Break down the logic of the source code.\n"
        "3. Translate each logical component into {target_language}.\n"
        "4. Combine components into the final function.\n"
        "5. Ensure your translation is syntactically correct and passes all test cases.\n\n"
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