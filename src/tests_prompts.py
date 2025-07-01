class TestBasePrompt:
    @staticmethod
    def prompt(context):
        raise NotImplementedError

class GenerateTestCasesPromptJava(TestBasePrompt):
    SYSTEM_PROMPT = (
        "You are a proficient Java developer and an expert in Test-Driven development. "
        "Your primary goal is to write clean, efficient, and maintainable Java test cases. "
    )

    USER_PROMPT = (
        "Write exactly 5 test cases for the following Java code in JUnit 5. "
        "Ensure that the tests cover all edge cases and functionalities. "
        "Java code:\n"
        "\n{code}\n"
        "Return only the test cases without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": GenerateTestCasesPromptJava.SYSTEM_PROMPT},
            {"role": "user", "content": GenerateTestCasesPromptJava.USER_PROMPT.format(**context)}
        ]

class GenerateTestCasesPromptPython(TestBasePrompt):
    SYSTEM_PROMPT = (
        "You are a proficient Python developer and an expert in Test-Driven development. "
        "Your primary goal is to write clean, efficient, and maintainable Python test cases. "
    )

    USER_PROMPT = (
        "Write exactly 5 test cases for the following Python code in unittest. "
        "Ensure that the tests cover all edge cases and functionalities. "
        "Python code:\n"
        "\n{code}\n"
        "Return only the test cases without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": GenerateTestCasesPromptPython.SYSTEM_PROMPT},
            {"role": "user", "content": GenerateTestCasesPromptPython.USER_PROMPT.format(**context)}
        ]

class GenerateTestCasesPromptJavaScript(TestBasePrompt):
    SYSTEM_PROMPT = (
        "You are a proficient JavaScript developer and an expert in Test-Driven development. "
        "Your primary goal is to write clean, efficient, and maintainable JavaScript test cases. "
    )

    USER_PROMPT = (
        "Write exactly 5 test cases for the following Java code in Jest. "
        "Ensure that the tests cover all edge cases and functionalities. "
        "Java code:\n"
        "\n{code}\n"
        "Return only the test cases without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": GenerateTestCasesPromptJavaScript.SYSTEM_PROMPT},
            {"role": "user", "content": GenerateTestCasesPromptJavaScript.USER_PROMPT.format(**context)}
        ]

class GenerateTestCasesPromptCPP(TestBasePrompt):
    SYSTEM_PROMPT = (
        "You are a proficient C++ developer and an expert in Test-Driven development. "
        "Your primary goal is to write clean, efficient, and maintainable C++ test cases. "
    )

    USER_PROMPT = (
        "Write exactly 5 test cases for the following C++ code in Google Test. "
        "Ensure that the tests cover all edge cases and functionalities. "
        "C++ code:\n"
        "\n{code}\n"
        "Return only the test cases without additional comments or explanations."
    )

    @staticmethod
    def prompt(context):
        return [
            {"role": "system", "content": GenerateTestCasesPromptCPP.SYSTEM_PROMPT},
            {"role": "user", "content": GenerateTestCasesPromptCPP.USER_PROMPT.format(**context)}
        ]