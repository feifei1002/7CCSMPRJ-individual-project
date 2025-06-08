from src.code_runner import CodeRunner


def execute_code_and_tests(file_path, language, test_dataset, index=0):
    execution_result = {
        "compilation_success": False,
        "tests_passed": False,
        "output": "",
        "error": ""
    }

    try:
        success, output, error = CodeRunner.execute(language, file_path)
        execution_result["compilation_success"] = success
        execution_result["output"] = output
        execution_result["error"] = error

        # Common error indicators across languages
        error_indicators = [
            "AssertionError",
            "Error:",
            "error:",
            "Exception",
            "Failed"
        ]

        # Check if any error indicators are present
        has_errors = any(indicator in output or indicator in error for indicator in error_indicators)

        # Test success conditions
        if success and not has_errors:
            if language == "JavaScript":
                execution_result["tests_passed"] = "PASS" in output or not error
            elif language == "Python":
                execution_result["tests_passed"] = not error and "AssertionError" not in output
            elif language == "Java":
                execution_result["tests_passed"] = not error and "Exception" not in output
            elif language == "C++" or language == "Go":
                execution_result["tests_passed"] = not error
            else:
                # Default case
                execution_result["tests_passed"] = success and not error

    except Exception as e:
        execution_result["error"] = str(e)
        execution_result["compilation_success"] = False
        execution_result["tests_passed"] = False

    return execution_result