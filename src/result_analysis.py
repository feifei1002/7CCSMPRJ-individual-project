import os
import re

from prettytable import PrettyTable
import matplotlib.pyplot as plt


def parse_file_info(filename):
    # Handle Windows path separators
    filename = filename.replace('\\', '/')

    try:
        # Extract path components
        parts = filename.split('/')

        # Get language pair from directory name
        lang_dir = next(part for part in parts if '_to_' in part)
        languages = lang_dir.split('_to_')
        source_language = languages[0]
        target_language = languages[1]

        # Get filename without extension
        file_name = parts[-1].replace('.txt', '')
        name_parts = file_name.split('_')

        # Last part is the model name
        llm = name_parts[-1]
        model_mapping = {
            "Mistral": "Codestral-2501",
            "OpenAI": "GPT-4o-mini",
            "Claude": "Claude 3.5 Haiku",
            "Gemini": "Gemini 2.0 Flash",
            "DeepSeek": "DeepSeek-V3"
        }
        llm = model_mapping.get(llm, llm)

        # Everything else is the prompt strategy
        txt_file = '_'.join(name_parts[:-1])
        return txt_file, llm, source_language, target_language

    except (IndexError, StopIteration):
        print(f"Error parsing filename: {filename}")
        return None, None, None, None

def calculate_llm_generated_test_rate(filename):
    total_problems = 0
    successful_compilations = 0
    tests_passed_count = 0
    total_tests_count = 0
    failed_compilations = 0

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, '..', filename)

    try:
        with open(file_path, 'r') as f:
            content = f.read()
            problems = content.split('Problem ')
            problems = [p for p in problems if p.strip() and ':' in p]
            total_problems = len(problems)

            for problem in problems:
                test_pattern = r"Tests passed: (\d+)/(\d+)"
                matches = re.search(test_pattern, problem)
                if matches:
                    passed = int(matches.group(1))
                    total = int(matches.group(2))
                    tests_passed_count += passed
                    total_tests_count += total
                if "Compilation successful: True" in problem:
                    successful_compilations += 1
                elif "Compilation successful: False" in problem:
                    failed_compilations += 1

        success_rate = (successful_compilations / total_problems) * 100 if total_problems > 0 else 0
        tests_passed_rate = (tests_passed_count / total_tests_count) * 100 if total_tests_count > 0 else 0
        return (success_rate, tests_passed_rate, total_problems,
                successful_compilations, failed_compilations,
                tests_passed_count, total_tests_count - tests_passed_count)
    except FileNotFoundError:
        return None, 0, 0, 0, 0, 0, 0
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return None, 0, 0, 0, 0, 0, 0

def calculate_provided_test_rate(filename):
    total_problems = 0
    successful_compilations = 0
    tests_passed = 0
    tests_failed = 0
    failed_compilations = 0

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, '..', filename)

    try:
        with open(file_path, 'r') as f:
            content = f.read()
            problems = content.split('--------------------------------------------------')

            for problem in problems:
                if problem.strip():
                    total_problems += 1
                    if "Compilation successful: True" in problem:
                        successful_compilations += 1
                        if "Tests passed: True" in problem:
                            tests_passed += 1
                        elif "Tests passed: False" in problem:
                            tests_failed += 1
                    elif "Compilation successful: False" in problem:
                        failed_compilations += 1

        success_rate = (successful_compilations / total_problems) * 100 if total_problems > 0 else 0
        tests_passed_rate = (tests_passed / total_problems) * 100 if total_problems > 0 else 0
        return success_rate, tests_passed_rate, total_problems, successful_compilations, failed_compilations, tests_passed, tests_failed

    except FileNotFoundError:
        return None, 0, 0
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return None, 0, 0


def save_table_as_image(result_table, filename):
    # Convert PrettyTable data to list of lists
    table_data = [result_table.field_names]  # Add headers
    table_data.extend(result_table._rows)  # Add rows

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, len(table_data) * 0.25))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1) # Remove all margins
    ax.axis('tight')
    ax.axis('off')

    # Add title
    strategy_name = os.path.basename(filename).replace('_results.png', '').replace('_', ' ')
    plt.title(strategy_name, fontsize=12, fontweight='bold', fontfamily='Arial', pad=1)

    # Calculate dynamic column widths based on number of columns
    num_columns = len(table_data[0])
    # First two columns (Direction and Strategy) get more width
    col_widths = [0.2, 0.2] + [0.6 / (num_columns - 2)] * (num_columns - 2)

    # Create table
    result_table = ax.table(cellText=table_data,
                            cellLoc='center',
                            loc='center',
                            bbox=[0, -0.05, 1, 1], # Adjust table position up
                            colWidths=col_widths)

    # Adjust table properties
    result_table.auto_set_font_size(False)
    result_table.set_fontsize(9)
    result_table.scale(1.2, 1)

    for pos, cell in result_table._cells.items():
        cell.set_facecolor('white')
        # cell.set_facecolor('none')
        if pos[0] == 0:
            cell.set_text_props(fontfamily='Arial', fontsize=9, weight='bold', color='black')
        else:
            cell.set_text_props(fontfamily='Arial', fontsize=9, color='black')

    plt.savefig(filename, bbox_inches='tight', dpi=300, pad_inches=0.01)
    plt.close()


def create_combined_summary_table(results):
    # Create table
    summary_table = PrettyTable()

    # Get unique LLMs for column headers
    llms = sorted(list(set(result['model'] for result in results)))

    # Set up field names with subcolumns for each LLM
    field_names = ["Direction", "Prompt Strategy"]
    for llm in llms:
        field_names.extend([f"{llm}\nComp%", f"{llm}\nTest%"])

    summary_table.field_names = field_names

    # Group results by direction and strategy
    grouped_results = {}
    for result in results:
        key = (result['direction'], result['strategy'])
        if key not in grouped_results:
            grouped_results[key] = {}
        grouped_results[key][result['model']] = {
            'compile_rate': result['success_rate'],
            'test_rate': result['test_pass_rate']
        }

    # Sort keys for consistent display
    sorted_keys = sorted(grouped_results.keys())

    # Add rows to table
    for direction, strategy in sorted_keys:
        row = [direction, strategy]
        for llm in llms:
            rates = grouped_results.get((direction, strategy), {}).get(llm, {})
            row.append(f"{rates.get('compile_rate', 0):.2f}")
            row.append(f"{rates.get('test_rate', 0):.2f}")
        summary_table.add_row(row)

    print("\nSummary of Results (Compilation % and Test Pass %):")
    print(summary_table)

    # Save table as image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, '..', 'tables')
    summary_filename = os.path.join(output_dir, 'combined_summary.png')
    save_table_as_image(summary_table, summary_filename)

# Main execution code
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, '..')

    # Create a dictionary to store tables by prompt strategy
    strategy_tables = {}

    # Initialize field names for all tables
    field_names = ["LLM Model", "Compile Success Rate (%)", "Success/Total", "Fail/Total", "Tests Passed Rate (%)", "Tests Passed/Total", "Tests Failed/Total"]

    # Walk through directories to find result files
    results = []
    for root, _, files in os.walk(results_dir):
        for file in files:
            if file.endswith('.txt'):
                rel_path = os.path.relpath(os.path.join(root, file), results_dir)
                # Skip error analysis report files
                if 'error_analysis_report' in rel_path:
                    continue
                if '_to_' in rel_path:
                    info = parse_file_info(rel_path)
                    if all(info):
                        prompt_strategy, llm_model, source_lang, target_lang = info
                        if "LLMGeneratedTests" in rel_path:
                            rates = calculate_llm_generated_test_rate(rel_path)
                        else:
                            rates = calculate_provided_test_rate(rel_path)

                        if rates[0] is not None:
                            success_rate, test_pass_rate, total, successful, failed, test_passed, test_failed = rates
                            direction = f"{source_lang} to {target_lang}"
                            results.append({
                                'strategy': prompt_strategy,
                                'direction': direction,
                                'model': llm_model,
                                'source': source_lang,
                                'target': target_lang,
                                'total': total,
                                'success_rate': success_rate,
                                'successful': successful,
                                'failed': failed,
                                'test_pass_rate': test_pass_rate,
                                'tests_passed': test_passed,
                                'tests_failed': test_failed
                            })

    # Group results by strategy and create tables
    for result in results:
        strategy = result['strategy']
        direction = result['direction']
        key = (strategy, direction)

        # Initialize table if not already done
        if key not in strategy_tables:
            table = PrettyTable()
            table.field_names = field_names
            strategy_tables[key] = table

        # Add row to corresponding strategy table
        strategy_tables[key].add_row([
            result['model'],
            f"{result['success_rate']:.2f}",
            f"{result['successful']}/{result['total']}",
            f"{result['failed']}/{result['total']}",
            f"{result['test_pass_rate']:.2f}",
            f"{result['tests_passed']}/{result['tests_failed'] + result['tests_passed']}",
            f"{result['tests_failed']}/{result['tests_failed'] + result['tests_passed']}"
        ])

    # Create output directory for tables if it doesn't exist
    output_dir = os.path.join(script_dir, '..', 'tables')
    os.makedirs(output_dir, exist_ok=True)

    # Save each strategy table as a separate image
    for (strategy, direction), table in strategy_tables.items():
        print(f"\nResults for {strategy} ({direction}):")
        print(table)

        # Create filename-safe version of strategy name
        safe_strategy_name = strategy.replace(' ', '_').replace('/', '_')
        safe_direction = direction.title()
        image_filename = os.path.join(output_dir, f'{safe_strategy_name}_{safe_direction}_results.png')
        save_table_as_image(table, image_filename)

    create_combined_summary_table(results)

if __name__ == '__main__':
    main()