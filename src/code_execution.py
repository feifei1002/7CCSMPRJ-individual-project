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
            dir_path = os.path.dirname(os.path.abspath(file_path))

            if "Main.java" in file_path:
                compile_cmd = ["javac", file_path]
                p = run(compile_cmd, capture_output=True, text=True)
                execution_result["compilation_success"] = p.returncode == 0
                if not execution_result["compilation_success"]:
                    execution_result["compilation_error"] = p.stderr.strip()
                    return execution_result
                try:
                    run_cmd = ["java", "-cp", dir_path, "Main"]
                    print(f"Running command: {' '.join(run_cmd)}")  # Debug print
                    p = run(run_cmd, capture_output=True, text=True)
                    execution_result["output"] = p.stdout
                    execution_result["tests_passed"] = p.returncode == 0
                    if not execution_result["tests_passed"]:
                        execution_result["test_error"] = p.stderr if p.stderr else p.stdout
                except Exception as e:
                    execution_result["test_error"] = f"Execution error: {str(e)}"
                    execution_result["tests_passed"] = False
            else:
                junit_jar = "../lib/junit-platform-console-standalone-1.13.0.jar"
                java_files = [f for f in os.listdir(dir_path) if f.endswith('.java') and f != 'Main.java']
                source_file = next(f for f in java_files if not f.endswith('Test.java'))
                test_file = next(f for f in java_files if f.endswith('Test.java'))

                # Compile Java code
                compile_cmd = ["javac", "-cp", junit_jar,
                               os.path.join(dir_path, source_file),
                               os.path.join(dir_path, test_file)]
                print(f"Running compilation command: {' '.join(compile_cmd)}")  # Debug print
                p = run(compile_cmd, capture_output=True, text=True)
                execution_result["compilation_success"] = p.returncode == 0

                if not execution_result["compilation_success"]:
                    execution_result["error"] = p.stderr
                    return execution_result

                # Run tests if compilation successful
                if file_path.endswith('.java') and 'Main.java' not in file_path:
                    try:
                        test_cmd = ["java", "-jar", junit_jar,
                                    "--class-path", dir_path,
                                    "--scan-class-path"]
                        current_dir = os.getcwd()
                        os.chdir(dir_path)
                        p = run(test_cmd, capture_output=True, text=True)
                        os.chdir(current_dir)
                        output = p.stdout + p.stderr
                        execution_result["results"] = output

                        # Parse test results
                        tests_found = re.search(r'\[(\s*\d+) tests found\s*\]', output)
                        tests_passed = re.search(r'\[(\s*\d+) tests successful\s*\]', output)
                        if tests_found and tests_passed:
                            total = int(tests_found.group(1))
                            passed = int(tests_passed.group(1))
                            execution_result["test_stats"] = f"{passed}/{total}"
                            execution_result["tests_passed"] = passed == total

                        if not execution_result["tests_passed"]:
                            execution_result["test_error"] = output
                    except Exception as e:
                        execution_result["test_error"] = f"Test execution error: {str(e)}"
                        execution_result["tests_passed"] = False

    except Exception as e:
        execution_result["compilation_success"] = False
        execution_result["compilation_error"] = f"Execution error: {str(e)}"


    finally:
        # Clean up generated class files for Java
        if language == "Java":
            for f in os.listdir(dir_path):
                if f.endswith('.class'):
                    try:
                        os.remove(os.path.join(dir_path, f))
                    except:
                        pass

    print(f"Execution result: {execution_result}\n")
    return execution_result