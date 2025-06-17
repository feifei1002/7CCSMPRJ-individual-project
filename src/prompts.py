class BasePrompt:
    @staticmethod
    def prompt(context):
        raise NotImplementedError


class InitialPrompt(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant that follow test-driven development (TDD) principles "
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
            {"role": "system", "content": InitialPrompt.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": InitialPrompt.USER_PROMPT.format(**context)}
        ]


class RoleBasedPrompt(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a senior software engineer in both {source_language} and {target_language} development. "
        "You specialize in cross-language code translation and test-driven development (TDD) principles."
        "You are known for writing clean and maintainable code. "
        "Your primary goal is to translate {source_language} code to {target_language} accurately and passes all provided test cases. "

    )

    USER_PROMPT = (
        "As an expert in {source_language} to {target_language} translation, "
        "translate the following {source_language} code to {target_language} while ensuring it passes the provided test cases. "
        "{source_language} code:\n"
        "\n{code}\n"
        "{target_language} test cases:\n"
        "\n{test_cases}\n"
        "\n{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Return only the translated code without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": RoleBasedPrompt.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": RoleBasedPrompt.USER_PROMPT.format(**context)}
        ]


class TestFirstPrompt(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a code translation assistant that follows test-driven development (TDD) principles. "
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
            {"role": "system", "content": TestFirstPrompt.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": TestFirstPrompt.USER_PROMPT.format(**context)}
        ]


class StepByStepPrompt(BasePrompt):
    SYSTEM_PROMPT = (
        "You are a methodical programmer who breaks down complex tasks into manageable steps. "
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
            {"role": "system", "content": StepByStepPrompt.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": StepByStepPrompt.USER_PROMPT.format(**context)}
        ]


class DirectMappingPrompt(BasePrompt):
    SYSTEM_PROMPT = (
        "You are an assistant specialize in structural code translation,"
        "maintaining similar architecture and logic between {source_language} and {target_language} while adapting syntax. "
        "You believe in preserving the original code's structure and logic flow to maintain clarity and debugging ease. "
    )

    USER_PROMPT = (
        "Translate the following {source_language} code to {target_language} using direct structural mapping while ensuring it passes the provided test cases. "
        "{source_language} code:\n"
        "\n{code}\n"
        "{target_language} test cases:\n"
        "\n{test_cases}\n"
        "\n{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Maintain similar structure by mapping:\n"
        "Classes -> Classes\n"
        "Methods -> Methods\n"
        "Functions -> Functions\n"
        "Variables -> Variables\n"
        "Control flow -> Same control flow patterns\n"
        "Logic structure -> Identical logic structure\n"
        "Return only the translated code without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": DirectMappingPrompt.SYSTEM_PROMPT.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": DirectMappingPrompt.USER_PROMPT.format(**context)}
        ]