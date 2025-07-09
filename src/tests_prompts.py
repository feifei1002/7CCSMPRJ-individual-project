class TestBasePrompt:
    @staticmethod
    def prompt(context, num_tests=5):
        raise NotImplementedError

class GenerateTestCasesPromptJava(TestBasePrompt):
    SYSTEM_PROMPT = (
        "You are a proficient Java developer and an expert in Test-Driven development. "
        "Your primary goal is to write clean, efficient, and maintainable Java test cases. "
    )

    USER_PROMPT = (
        "Write exactly {num_tests} test cases for the following Java code in JUnit 5. "
        "Ensure that the tests cover all edge cases and functionalities. "
        "Java code:\n"
        "\n{code}\n"
        "Return only the test cases without additional comments or explanations."
    )

    @staticmethod
    def prompt(context, num_tests=5):
        context_with_num_tests = {**context, 'num_tests': num_tests}
        return [
            {"role": "system", "content": GenerateTestCasesPromptJava.SYSTEM_PROMPT},
            {"role": "user", "content": GenerateTestCasesPromptJava.USER_PROMPT.format(**context_with_num_tests)}
        ]

class GenerateTestCasesPromptPython(TestBasePrompt):
    SYSTEM_PROMPT = (
        "You are a proficient Python developer and an expert in Test-Driven development. "
        "Your primary goal is to write clean, efficient, and maintainable Python test cases. "
    )

    USER_PROMPT = (
        "Write exactly {num_tests} test cases for the following Python code in unittest. "
        "Ensure that the tests cover all edge cases and functionalities. "
        "Python code:\n"
        "\n{code}\n"
        "Return only the test cases without additional comments or explanations."
    )

    @staticmethod
    def prompt(context, num_tests=5):
        context_with_num_tests = {**context, 'num_tests': num_tests}
        return [
            {"role": "system", "content": GenerateTestCasesPromptPython.SYSTEM_PROMPT},
            {"role": "user", "content": GenerateTestCasesPromptPython.USER_PROMPT.format(**context_with_num_tests)}
        ]

class GenerateTestCasesPromptJavaScript(TestBasePrompt):
    SYSTEM_PROMPT = (
        "You are a proficient JavaScript developer and an expert in Test-Driven development. "
        "Your primary goal is to write clean, efficient, and maintainable JavaScript test cases. "
    )

    USER_PROMPT = (
        "Write exactly {num_tests} test cases for the following Java code in Jest. "
        "Ensure that the tests cover all edge cases and functionalities. "
        "Java code:\n"
        "\n{code}\n"
        "Return only the test cases without additional comments or explanations."
    )

    @staticmethod
    def prompt(context, num_tests=5):
        context_with_num_tests = {**context, 'num_tests': num_tests}
        return [
            {"role": "system", "content": GenerateTestCasesPromptJavaScript.SYSTEM_PROMPT},
            {"role": "user", "content": GenerateTestCasesPromptJavaScript.USER_PROMPT.format(**context_with_num_tests)}
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