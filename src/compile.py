import os
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
            "Codestral": "Codestral-2501",
            "OpenAI": "GPT-4o-mini",
            "Claude": "Claude 3.5 Haiku",
            "Gemini": "Gemini 1.5 Pro",
            "DeepSeek": "DeepSeek-R1"
        }
        llm = model_mapping.get(llm, llm)

        # Everything else is the prompt strategy
        prompt = '_'.join(name_parts[:-1])

        return prompt, llm, source_language, target_language

    except (IndexError, StopIteration):
        print(f"Error parsing filename: {filename}")
        return None, None, None, None


def calculate_success_rate(filename):
    total_problems = 0
    successful_compilations = 0
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
                    elif "Compilation successful: False" in problem:
                        failed_compilations += 1

        success_rate = (successful_compilations / total_problems) * 100 if total_problems > 0 else 0
        return success_rate, total_problems, successful_compilations, failed_compilations

    except FileNotFoundError:
        return None, 0, 0
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return None, 0, 0


def save_table_as_image(result_table, filename='results_table.png'):
    # Convert PrettyTable data to list of lists
    table_data = [result_table.field_names]  # Add headers
    table_data.extend(result_table._rows)     # Add rows

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, len(table_data) * 0.5 + 1))
    fig.patch.set_alpha(0.0)  # Make the figure background transparent
    ax.patch.set_alpha(0.0)  # Make the axis background transparent
    ax.axis('tight')
    ax.axis('off')

    # Create table
    result_table = ax.table(cellText=table_data,
                    cellLoc='center',
                    loc='center',
                    colWidths=[0.2, 0.15, 0.15, 0.15, 0.15, 0.1, 0.1])

    # Adjust table properties
    result_table.auto_set_font_size(False)
    result_table.set_fontsize(9)
    result_table.scale(1.2, 1.5)

    for pos, cell in result_table._cells.items():
        cell.set_facecolor('none')  # Make all cells transparent
        if pos[0] == 0:  # Header row
            cell.set_text_props(fontfamily='Arial', fontsize=9, weight='bold', color='black')
        else:  # Data rows
            cell.set_text_props(fontfamily='Arial', fontsize=9, color='black')

    # Save to file
    plt.savefig(filename, bbox_inches='tight', dpi=300, pad_inches=0.1)
    plt.close()


# Main execution code
script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(script_dir, '..')

# Create table
table = PrettyTable()
table.field_names = ["Prompt Strategy", "LLM Model", "Source Language", "Target Language",
                     "Success Rate (%)", "Successful/Total", "Failure/Total"]

# Walk through directories to find result files
for root, _, files in os.walk(results_dir):
    for file in files:
        if file.endswith('.txt'):
            rel_path = os.path.relpath(os.path.join(root, file), results_dir)
            if '_to_' in rel_path:
                info = parse_file_info(rel_path)
                if all(info):  # Check if parsing was successful
                    prompt_strategy, llm_model, source_lang, target_lang = info
                    success_rate, total, successful, failed = calculate_success_rate(rel_path)

                    if success_rate is not None:
                        table.add_row([
                            prompt_strategy,
                            llm_model,
                            source_lang,
                            target_lang,
                            f"{success_rate:.2f}",
                            f"{successful}/{total}",
                            f"{failed}/{total}"
                        ])

# Print the table
print(table)

# Save the table as an image
save_table_as_image(table)