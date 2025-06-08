class CodeTransPrompt:
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
            {"role": "system", "content": CodeTransPrompt.system_prompt.format(
                source_language=context["source_language"],
                target_language=context["target_language"]
            )},
            {"role": "user", "content": CodeTransPrompt.user_prompt.format(**context)}
        ]