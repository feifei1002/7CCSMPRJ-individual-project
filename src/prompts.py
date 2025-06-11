class BasePrompt:
    @staticmethod
    def prompt(context):
        raise NotImplementedError

class InitialPrompt(BasePrompt):
    system_prompt = (
        "Translate the following {source_language} code to {target_language}, "
        "using the provided test cases. "
        "Do not return anything other than the translated code. "
    )
    user_prompt = (
        "{source_language} code:\n"
        "\n{code}\n"
        "Test Cases:\n"
        "\n{test_cases}\n"
        "\n{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": InitialPrompt.system_prompt.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": InitialPrompt.user_prompt.format(**context)}
        ]

class RoleBasedPrompt(BasePrompt):
    system_prompt = (
        "You are an expert in code translation and follow test-driven development (TDD) principles. "
        "Translate the following {source_language} code to {target_language}. Ensure that your translation is executable "
        "and passed the provided test cases. "
    )

    user_prompt = (
        "Here is the {source_language} code:\n"
        "\n{code}\n"
        "Test Cases:\n"
        "\n{test_cases}\n"
        "Translate it to {target_language} and embed the translated code within the following function declaration:\n"
        "\n{declaration}\n    # INSERT TRANSLATED CODE HERE\n"
        "Return only the full {target_language} code with no extra comments, explanation and markers."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": RoleBasedPrompt.system_prompt.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": RoleBasedPrompt.user_prompt.format(**context)}
        ]