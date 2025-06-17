import os
from collections import defaultdict

import pandas as pd
from matplotlib import pyplot as plt


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


def create_error_table(analyzer, dir_name, report_dir) -> None:
    # Convert error data to a DataFrame
    error_data = defaultdict(lambda: defaultdict(int))

    for filepath, errors in analyzer.file_errors.items():
        model_name = os.path.basename(filepath).split('_')[0]  # Extract model name
        for error_type, count in errors.items():
            error_data[model_name][error_type] += count

    df = pd.DataFrame.from_dict(error_data, orient='index').fillna(0)

    # Create figure and axis
    table_data = [df.columns.tolist()] # Headers
    for index, row in df.iterrows():
        table_data.append([index] + row.astype(int).tolist())

    fig, ax = plt.subplots(figsize=(12, len(table_data) * 0.2))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1)
    ax.axis('tight')
    ax.axis('off')

    # Add title
    plt.title(f'Error Analysis Table for {dir_name}', fontsize=12, fontweight='bold', pad=1, fontfamily='Arial')

    # Create table
    cols = ['Model'] + df.columns.tolist()
    cell_data = [[index] + row.tolist() for index, row in df.iterrows()]
    table = ax.table(cellText=cell_data,
                     colLabels=cols,
                     cellLoc='center',
                     loc='center',
                     bbox=[0, -0.05, 1, 1])

    # Adjust table style
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1)

    for pos, cell in table._cells.items():
        cell.set_facecolor('none')  # Transparent background
        if pos[0] == 0:  # Header row
            cell.set_text_props(fontweight='bold', fontsize=9, color='black', fontfamily='Arial')
        else:
            cell.set_text_props(fontsize=9, color='black', fontfamily='Arial')


    # Save the figure
    plt.savefig(os.path.join(os.path.join(report_dir, f'error_table_{dir_name}.png')),
                bbox_inches='tight',
                dpi=300, pad_inches=0.01)
    plt.close()

def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(src_dir)
    report_dir = os.path.join(project_dir, 'report')
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
        report_path = os.path.join(report_dir, f'error_analysis_report_{dir_name}.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
            print(f"Error analysis complete. Report saved to '{report_path}'")
        create_error_table(analyzer, dir_name, report_dir)
        print(f"Error table image saved as 'error_table_{dir_name}.png'")


if __name__ == "__main__":
    main()