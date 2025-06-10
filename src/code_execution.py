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

        error_info = []
        if error:
            error_info.append(f"Runtime error: {error}")

        # Common error indicators across languages
        error_indicators = [
            "AssertionError",
            "Error:",
            "error:",
            "Exception",
            "Failed"
        ]

        for indicator in error_indicators:
            if indicator in output:
                error_info.append(f"Test outpur error: {output}")
                break

        execution_result["error"] = "\n".join(error_info)

        has_errors = bool(error_info)

        # Test success conditions
        if success and not has_errors:
            if language == "JavaScript":
                execution_result["tests_passed"] = "PASS" in output
            elif language == "Python":
                execution_result["tests_passed"] = "AssertionError" not in output
            elif language == "Java":
                execution_result["tests_passed"] = "Exception" not in output
            elif language == "C++" or language == "Go":
                execution_result["tests_passed"] = True
            else:
                # Default case
                execution_result["tests_passed"] = success

    except Exception as e:
        execution_result["error"] = f"Execution error: {str(e)}"
        execution_result["compilation_success"] = False
        execution_result["tests_passed"] = False

    return execution_result