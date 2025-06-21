import os
import re
from subprocess import run, PIPE


def execute_code_and_tests(file_path, language, test_dataset, index=0):
    """
    Execute code and run tests with improved compilation and execution checking.
    """

    print(f"\nExecuting file: {file_path}")
    print(f"Language: {language}")
    execution_result = {
        "compilation_success": False,
        "tests_passed": False,
        "compilation_error": "",
        "test_error": "",
        "output": "",
        "test_stats": "0/0"
    }

    try:
        if language == "Python":

            compile_cmd = ["python", "-m", "py_compile", file_path]
            p = run(compile_cmd, capture_output=True, text=True)
            execution_result["compilation_success"] = p.returncode == 0

            if not execution_result["compilation_success"]:
                execution_result["compilation_error"] = p.stderr.strip()
                return execution_result

            dir_path = os.path.dirname(file_path)

            if "solution.py" in file_path:
                try:
                    test_cmd = ["python", "-m", "unittest", "-v", "test_cases"]
                    env = os.environ.copy()
                    env["PYTHONPATH"] = dir_path + os.pathsep + env.get("PYTHONPATH", "")

                    # Change to the directory containing the files
                    current_dir = os.getcwd()
                    os.chdir(dir_path)

                    p = run(test_cmd, capture_output=True, text=True, env=env)

                    # Change back to original directory
                    os.chdir(current_dir)

                    output = p.stdout + p.stderr
                    failures = output.count('FAILED')
                    # Count total tests from test_cases.py
                    with open(os.path.join(dir_path, "test_cases.py"), "r") as f:
                        test_content = f.read()
                        total = len([line for line in test_content.split('\n')
                                 if line.strip().startswith('def test_')])

                    passed = total - failures
                    execution_result["results"] = output
                    execution_result["test_stats"] = f"{passed}/{total}"
                    execution_result["tests_passed"] = passed == total
                    execution_result["compilation_success"] = True
                    if not execution_result["tests_passed"]:
                        execution_result["test_error"] = p.stderr.strip() if p.stderr else p.stdout
                except Exception as e:
                    execution_result["test_error"] = f"Test execution error: {str(e)}"
                    execution_result["tests_passed"] = False
            else:
                try:
                    run_cmd = ["python", file_path]
                    p = run(run_cmd, capture_output=True, text=True)

                    execution_result["output"] = p.stdout
                    execution_result["tests_passed"] = p.returncode == 0 and "AssertionError" not in p.stdout
                    if not execution_result["tests_passed"]:
                        execution_result["test_error"] = p.stderr if p.stderr else p.stdout
                except Exception as e:
                    execution_result["test_error"] = f"Execution error: {str(e)}"
                    execution_result["tests_passed"] = False



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

    except Exception as e:
        execution_result["compilation_success"] = False
        execution_result["compilation_error"] = f"Execution error: {str(e)}"


    finally:
        # Clean up generated class files for Java
        if language == "Java":
            class_file = os.path.join(os.path.dirname(file_path), "Main.class")
            if os.path.exists(class_file):
                os.remove(class_file)

    print(f"Execution result: {execution_result}\n")
    return execution_result