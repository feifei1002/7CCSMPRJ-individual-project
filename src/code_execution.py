import os
import re
from subprocess import run, PIPE

def execute_code_and_tests(file_path: str, language: str, test_dataset: list, index: int, test_count: int = 0):
    """
    Execute code and run tests with improved compilation and execution checking.
    """

    print(f"Language: {language}")
    execution_result = {
        "compilation_success": False,
        "tests_passed": False,
        "compilation_error": "",
        "test_error": "",
        "output": "",
        "test_stats": f"0/0"
    }
    dir_path = os.path.dirname(file_path)
    try:
        if language == "Python":

            compile_cmd = ["python", "-m", "py_compile", file_path]
            p = run(compile_cmd, capture_output=True, text=True)
            execution_result["compilation_success"] = p.returncode == 0

            if not execution_result["compilation_success"]:
                execution_result["compilation_error"] = p.stderr.strip()
                return execution_result

            # dir_path = os.path.dirname(file_path)

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
                    total_tests = len(re.findall(r'test_.*\s\(.*\)\s\.{3}\s', output))
                    failed_tests = len(re.findall(r'FAIL: test_.*\s\(.*\)', output))
                    error_tests = len(re.findall(r'ERROR: test_.*\s\(.*\)', output))
                    passed_tests = total_tests - (failed_tests + error_tests)
                    # Count total tests from test_cases.py
                    with open(os.path.join(dir_path, "test_cases.py"), "r") as f:
                        test_content = f.read()
                        test_count = len([line for line in test_content.split('\n')
                                 if line.strip().startswith('def test_')])
                    execution_result["test_stats"] = f"0/{test_count}"

                    execution_result["results"] = output
                    execution_result["test_stats"] = f"{passed_tests}/{test_count}"
                    execution_result["tests_passed"] = passed_tests == test_count
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
            # test_count = 0

            if "Main.java" in file_path:
                compile_cmd = ["javac", file_path]
                p = run(compile_cmd, capture_output=True, text=True)
                execution_result["compilation_success"] = p.returncode == 0
                if not execution_result["compilation_success"]:
                    execution_result["compilation_error"] = p.stderr.strip()
                    return execution_result
                try:
                    run_cmd = ["java", "-cp", dir_path, "Main"]
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
                source_file = next(f for f in java_files if not f.endswith('Test.java') or f.startswith('Test'))
                test_file = next(f for f in java_files if f.endswith('Test.java') or f.startswith('Test'))

                # Count tests in the test file
                with open(os.path.join(dir_path, test_file)) as f:
                    test_content = f.read()
                    test_count = len(re.findall(r'@Test', test_content))
                execution_result["test_stats"] = f"0/{test_count}"

                # Compile Java code
                compile_source_cmd = ["javac", os.path.join(dir_path, source_file)]
                print(f"Compile source file: {' '.join(compile_source_cmd)}")  # Debug print
                p_source = run(compile_source_cmd, capture_output=True, text=True)
                execution_result["compilation_success"] = p_source.returncode == 0

                if not execution_result["compilation_success"]:
                    execution_result["error"] = p_source.stderr
                    return execution_result

                # Compile test code
                compile_test_cmd = ["javac", "-cp", junit_jar,
                                    os.path.join(dir_path, source_file),
                                    os.path.join(dir_path, test_file)]
                print(f"Compile with tests: {' '.join(compile_test_cmd)}")  # Debug print
                p_test = run(compile_test_cmd, capture_output=True, text=True)
                if p_test.returncode != 0:
                    execution_result["test_error"] = f"Compilation error: {p_test.stderr.strip()}"
                    execution_result["tests_passed"] = False
                    return execution_result

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
                    tests_passed = re.search(r'\[(\s*\d+) tests successful\s*\]', output)
                    if tests_passed:
                        passed = int(tests_passed.group(1) or 0)
                        execution_result["test_stats"] = f"{passed}/{test_count}"
                        execution_result["tests_passed"] = passed == test_count

                    test_failed = re.search(r'Failures \(\d+\):.*?(?=Test run finished)', output, re.DOTALL)
                    if not execution_result["tests_passed"]:
                        execution_result["test_error"] = test_failed.group(0) if test_failed else output
                except Exception as e:
                    execution_result["test_error"] = f"Test execution error: {str(e)}"
                    execution_result["tests_passed"] = False
                    execution_result["test_stats"] = f"0/{test_count}"


        elif language == "JavaScript":
            dir_path = os.path.dirname(file_path)
            project_root = os.path.dirname(os.path.dirname(file_path))
            compile_cmd = ["node", "--check", file_path]
            p = run(compile_cmd, capture_output=True, text=True)
            execution_result["compilation_success"] = p.returncode == 0

            if not execution_result["compilation_success"]:
                execution_result["compilation_error"] = p.stderr.strip()
                return execution_result

            if "solution.js" in file_path:
                try:
                    test_file = os.path.join(dir_path, "test_cases.js")
                    with open(test_file) as f:
                        test_content = f.read()
                        test_count = len(re.findall(r'test\(|it\(', test_content))
                    execution_result["test_stats"] = f"0/{test_count}"
                    test_cmd = ["npx", "jest", "--verbose", test_file]
                    p = run(test_cmd, capture_output=True, text=True, cwd=project_root, shell=True, encoding='utf-8')
                    output = p.stdout + p.stderr
                    test_summary = re.search(r'Tests:\s+(?:(\d+)\s+failed,\s+)?(?:(\d+)\s+passed,\s+)?(\d+)\s+total', output)
                    if test_summary:
                        passed = int(test_summary.group(2) or 0)
                        execution_result["test_stats"] = f"{passed}/{test_count}"
                        execution_result["tests_passed"] = passed == test_count

                    execution_result["results"] = output
                    execution_result["compilation_success"] = True
                    if not execution_result["tests_passed"]:
                        execution_result["test_error"] = p.stderr.strip() if p.stderr else p.stdout
                except Exception as e:
                    execution_result["test_error"] = f"Test execution error: {str(e)}"
                    execution_result["tests_passed"] = False
                    if test_count > 0:
                        execution_result["test_stats"] = f"0/{test_count}"
            else:
                try:
                    run_cmd = ["node", file_path]
                    p = run(run_cmd, capture_output=True, text=True)
                    execution_result["output"] = p.stdout
                    execution_result["tests_passed"] = p.returncode == 0
                    if not execution_result["tests_passed"]:
                        execution_result["test_error"] = p.stderr if p.stderr else p.stdout
                except Exception as e:
                    execution_result["test_error"] = f"Execution error: {str(e)}"
                    execution_result["tests_passed"] = False



    finally:
        try:
            if language == "Java":
                # Remove .class files and Java source files
                for f in os.listdir(dir_path):
                    if f.endswith(('.class', '.java')):
                        os.remove(os.path.join(dir_path, f))
            elif language == "Python":
                # Remove .pyc files and Python source files
                for f in os.listdir(dir_path):
                    if f.endswith(('.pyc', '.py')):
                        os.remove(os.path.join(dir_path, f))
                # Remove __pycache__ directory
                pycache_dir = os.path.join(dir_path, "__pycache__")
                if os.path.exists(pycache_dir):
                    for f in os.listdir(pycache_dir):
                        os.remove(os.path.join(pycache_dir, f))
                    os.rmdir(pycache_dir)
            elif language == "JavaScript":
                for f in os.listdir(dir_path):
                    if f.endswith('.js'):
                        os.remove(os.path.join(dir_path, f))
        except Exception as e:
            print(f"Warning: Failed to clean up some files: {str(e)}")

    print(f"Execution result: {execution_result}\n")
    return execution_result