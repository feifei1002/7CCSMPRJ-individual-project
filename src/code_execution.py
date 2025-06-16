import os
from subprocess import run, PIPE

from src.code_runner import CodeRunner

def execute_code_and_tests(file_path, language, test_dataset, index=0):
    """
    Execute code and run tests with improved compilation and execution checking.
    """
    execution_result = {
        "compilation_success": False,
        "tests_passed": False,
        "output": "",
        "error": ""
    }

    try:
        if language == "Python":
            # Check compilation first
            compile_cmd = ["python", "-m", "py_compile", file_path]
            p = run(compile_cmd, stderr=PIPE)
            execution_result["compilation_success"] = p.returncode == 0

            if not execution_result["compilation_success"]:
                execution_result["error"] = p.stderr.decode("utf-8")
                return execution_result

            # Run tests if compilation successful
            run_cmd = ["python", file_path]
            p = run(run_cmd, stderr=PIPE, stdout=PIPE)
            execution_result["output"] = p.stdout.decode("utf-8")
            if p.stderr:
                execution_result["error"] = p.stderr.decode("utf-8")

            # Check test results
            execution_result["tests_passed"] = (
                    p.returncode == 0
                    and "AssertionError" not in execution_result["output"]
                    and "Error:" not in execution_result["output"]
            )

        elif language == "Java":
            # Compile Java code
            compile_cmd = ["javac", file_path]
            p = run(compile_cmd, stderr=PIPE)
            execution_result["compilation_success"] = p.returncode == 0

            if not execution_result["compilation_success"]:
                execution_result["error"] = p.stderr.decode("utf-8")
                return execution_result

            # Run tests if compilation successful
            class_name = "Main"
            run_cmd = ["java", "-cp", os.path.dirname(file_path), class_name]
            p = run(run_cmd, stderr=PIPE, stdout=PIPE)
            execution_result["output"] = p.stdout.decode("utf-8")
            if p.stderr:
                execution_result["error"] = p.stderr.decode("utf-8")

            # Check test results
            execution_result["tests_passed"] = (
                    p.returncode == 0
                    and "Exception" not in execution_result["output"]
                    and "Error:" not in execution_result["output"]
            )

        else:
            # Existing handling for other languages
            success, output, error = CodeRunner.execute(language, file_path)
            execution_result["compilation_success"] = success
            execution_result["output"] = output
            execution_result["error"] = error
            execution_result["tests_passed"] = success and not error

    except Exception as e:
        execution_result["error"] = f"Execution error: {str(e)}"
        execution_result["compilation_success"] = False
        execution_result["tests_passed"] = False

    finally:
        # Clean up generated class files for Java
        if language == "Java":
            class_file = os.path.join(os.path.dirname(file_path), "Main.class")
            if os.path.exists(class_file):
                os.remove(class_file)

    return execution_result