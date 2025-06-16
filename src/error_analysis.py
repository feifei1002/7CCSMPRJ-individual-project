import os
from collections import defaultdict


class ErrorAnalysis:
    def __init__(self):
        self.file_errors = defaultdict(lambda: defaultdict(int))

    def generate_report(self) -> str:
        report = "Error Analysis Report by File\n"
        report += "==========================\n\n"

        for filepath, errors in self.file_errors.items():
            filename = os.path.basename(filepath)
            report += f"File: {filename}\n"
            report += "-" * (len(filename) + 6) + "\n"

            if not errors:
                report += "No errors found.\n"
            else:
                total = sum(errors.values())
                report += f"Total errors: {total}\n\n"
                for error_type, count in sorted(errors.items()):
                    report += f"{count}x: {error_type}\n"
            report += "\n"

        return report

class JavaToPythonErrorAnalysis(ErrorAnalysis):
    def analyze_file(self, filepath: str) -> None:
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                problems = content.split('--------------------------------------------------')

                for problem in problems:
                    if 'Error:' in problem:
                        error_msg = problem.split('Error:', 1)[1].strip()
                        # Extract error type from the error message
                        if 'IndentationError:' in problem:
                            error_type = 'IndentationError'
                        elif 'NameError:' in problem:
                            error_type = 'NameError'
                        elif 'SyntaxError:' in problem:
                            error_type = 'SyntaxError'
                        elif 'TypeError:' in problem:
                            error_type = 'TypeError'
                        elif 'AttributeError:' in problem:
                            error_type = 'AttributeError'
                        else:
                            error_type = 'Other Error'

                        self.file_errors[filepath][error_type] += 1

        except Exception as e:
            print(f"Error reading {filepath}: {str(e)}")

class PythonToJavaErrorAnalysis(ErrorAnalysis):
    def analyze_file(self, filepath: str) -> None:
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                problems = content.split('--------------------------------------------------')

                for problem in problems:
                    if 'Error:' in problem:
                        error_msg = problem.split('Error:', 1)[1].strip()
                        # Extract error type from Java compilation errors
                        if 'error:' in error_msg:
                            if 'cannot find symbol' in error_msg:
                                error_type = 'Symbol Not Found'
                            elif 'incompatible types' in error_msg:
                                error_type = 'Type Mismatch'
                            elif 'class, interface, enum, or record expected' in error_msg:
                                error_type = 'Invalid Class Declaration'
                            elif 'illegal start of expression' in error_msg:
                                error_type = 'Invalid Expression'
                            else:
                                error_type = 'Java Compilation Error'
                        else:
                            error_type = 'Other Error'

                        self.file_errors[filepath][error_type] += 1

        except Exception as e:
            print(f"Error reading {filepath}: {str(e)}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    directories = {
        "java_to_python": JavaToPythonErrorAnalysis(),
        "python_to_java": PythonToJavaErrorAnalysis()
    }
    for dir_name, analyzer in directories.items():
        results_dir = os.path.join(project_dir, dir_name)

        # Analyze all txt files in the directory
        for filename in os.listdir(results_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(results_dir, filename)
                analyzer.analyze_file(filepath)

        report = analyzer.generate_report()
        report_path = os.path.join(project_dir, f'error_analysis_report_{dir_name}.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
            print(f"Error analysis complete. Report saved to '{report_path}'")


if __name__ == "__main__":
    main()