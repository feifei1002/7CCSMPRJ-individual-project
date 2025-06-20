import os
from collections import defaultdict
from typing import List, Dict, Tuple

import numpy as np
from matplotlib import pyplot as plt
from prettytable import PrettyTable


class RankingAnalysis:
    def __init__(self):
        self.results = defaultdict(lambda: defaultdict(list))

    def analyze_results(self, results_dir: str) -> None:
        direction = "java_to_python" if "java_to_python" in results_dir else "python_to_java"

        for filename in os.listdir(results_dir):
            if filename.endswith('.txt'):
                strategy_name = filename.split('_')[0]
                model_name = filename.split('_')[1].replace('.txt', '')

                filepath = os.path.join(results_dir, filename)
                success_rate, test_pass_rate = self._calculate_rates(filepath)

                self.results[direction][model_name].append({
                    'strategy': strategy_name,
                    'success_rate': success_rate,
                    'test_pass_rate': test_pass_rate
                })

    def _calculate_rates(self, filepath: str) -> Tuple[float, float]:
        total = successful_compilations = successful_tests = 0

        with open(filepath, 'r') as f:
            content = f.read()
            problems = content.split('-' * 50)

            for problem in problems:
                if not problem.strip():
                    continue

                total += 1
                if 'Compilation successful: True' in problem:
                    successful_compilations += 1
                if 'Tests passed: True' in problem:
                    successful_tests += 1

        success_rate = (successful_compilations / total) * 100 if total > 0 else 0
        test_pass_rate = (successful_tests / total) * 100 if total > 0 else 0

        return success_rate, test_pass_rate

    def generate_rankings(self) -> str:
        report = "Strategy Rankings Report\n"
        report += "=====================\n\n"

        # Add strategy rankings by direction
        report += "Strategy Rankings By Direction\n"
        report += "==========================\n\n"

        for direction in self.results.keys():
            direction_stats = self._calculate_direction_stats(direction)
            report += f"{direction.replace('_', ' ').title()} Strategy Rankings\n"
            report += "=" * 40 + "\n"
            report += self._create_strategy_ranking_table(f"{direction.replace('_', ' ').title()}", direction_stats)
            report += "\n"

        # Strategy-specific rankings by direction
        report += "Detailed Strategy Performance By Direction\n"
        report += "=====================================\n\n"

        for direction in self.results.keys():
            report += f"\n{direction.replace('_', ' ').title()} Strategy Details\n"
            report += "=" * 40 + "\n\n"

            # Get all strategies
            strategies = set()
            for model_stats in self.results[direction].values():
                strategies.update(stat['strategy'] for stat in model_stats)

            # For each strategy, create a summary across all models
            for strategy in sorted(strategies):
                strategy_data = []
                for model, stats in self.results[direction].items():
                    strategy_stat = next((s for s in stats if s['strategy'] == strategy), None)
                    if strategy_stat:
                        strategy_data.append({
                            'model': model,
                            'success_rate': strategy_stat['success_rate'],
                            'test_pass_rate': strategy_stat['test_pass_rate']
                        })

                report += self._create_model_performance_table(strategy, strategy_data)

        return report

    def _calculate_direction_stats(self, direction: str) -> List[Dict]:
        strategy_stats = defaultdict(lambda: {'success_total': 0, 'test_total': 0, 'count': 0})

        for model in self.results[direction].keys():
            for result in self.results[direction][model]:
                strategy = result['strategy']
                strategy_stats[strategy]['success_total'] += result['success_rate']
                strategy_stats[strategy]['test_total'] += result['test_pass_rate']
                strategy_stats[strategy]['count'] += 1

        return [
            {
                'strategy': strategy,
                'success_rate': stats['success_total'] / stats['count'],
                'test_pass_rate': stats['test_total'] / stats['count']
            }
            for strategy, stats in strategy_stats.items()
        ]

    def _create_strategy_ranking_table(self, title: str, stats: List[Dict]) -> str:
        table = PrettyTable()
        table.field_names = ["Rank", "Strategy", "Success Rate", "Test Pass Rate"]

        sorted_stats = sorted(
            stats,
            key=lambda x: (x['success_rate'], x['test_pass_rate']),
            reverse=True
        )

        for rank, stat in enumerate(sorted_stats, 1):
            table.add_row([
                rank,
                stat['strategy'],
                f"{stat['success_rate']:.2f}%",
                f"{stat['test_pass_rate']:.2f}%"
            ])

        return f"\n{title}\n{'-' * len(title)}\n{table}\n\n"

    def _create_model_performance_table(self, strategy: str, stats: List[Dict]) -> str:
        table = PrettyTable()
        table.field_names = ["Rank", "Model", "Success Rate", "Test Pass Rate"]

        sorted_stats = sorted(
            stats,
            key=lambda x: (x['success_rate'], x['test_pass_rate']),
            reverse=True
        )

        for rank, stat in enumerate(sorted_stats, 1):
            table.add_row([
                rank,
                stat['model'],
                f"{stat['success_rate']:.2f}%",
                f"{stat['test_pass_rate']:.2f}%"
            ])

        return f"\n{strategy} Performance\n{'-' * len(strategy + ' Performance')}\n{table}\n\n"


    def create_visualization(self, report_dir: str) -> None:

        # Create direction-wise strategy performance charts
        for direction in self.results.keys():
            stats = self._calculate_direction_stats(direction)

            # Prepare data for plotting
            strategies = [stat['strategy'] for stat in stats]
            success_rates = [stat['success_rate'] for stat in stats]
            test_rates = [stat['test_pass_rate'] for stat in stats]

            # Create figure and axis
            plt.figure(figsize=(10, 6), facecolor='none')

            # Set width of bars and positions of bars
            width = 0.35
            x = np.arange(len(strategies))

            # Create bars
            plt.bar(x - width / 2, success_rates, width, label='Compile Success Rate', color='black')
            plt.bar(x + width / 2, test_rates, width, label='Test Pass Rate', color='lightgrey')

            # Set y-axis range from 0 to 100
            plt.ylim(0, 100)

            # Customize the plot
            plt.xlabel('Prompting Strategies', fontfamily='Arial', weight='bold')
            plt.ylabel('Rate (%)', fontfamily='Arial', weight='bold')
            plt.title(f'Strategy Performance - {direction.replace("_", " ").title()}',
                      fontfamily='Arial', weight='bold', pad=15)
            plt.xticks(x, strategies, ha='center', fontfamily='Arial')
            plt.yticks(fontfamily='Arial')
            plt.legend(prop={'family': 'Arial', 'weight': 'bold'})

            # Add value labels on top of bars
            for i, v in enumerate(success_rates):
                plt.text(i - width / 2, v + 0.25, f'{v:.1f}%', ha='center', va='bottom')
            for i, v in enumerate(test_rates):
                plt.text(i + width / 2, v + 0.25, f'{v:.1f}%', ha='center', va='bottom')

            # Adjust layout and save
            plt.tight_layout()
            plt.savefig(os.path.join(report_dir, f'strategy_performance_{direction}.png'), transparent=True)
            plt.close()

            # Create model performance charts for each strategy
            self._create_model_performance_charts(direction, report_dir)


    def _create_model_performance_charts(self, direction: str, report_dir: str) -> None:
        model_mapping = {
            "Mistral": "Codestral-2501",
            "OpenAI": "GPT-4o-mini",
            "Claude": "Claude 3.5 Haiku",
            "Gemini": "Gemini 2.0 Flash",
            "DeepSeek": "DeepSeek-V3"
        }
        strategies = set()
        for model_stats in self.results[direction].values():
            strategies.update(stat['strategy'] for stat in model_stats)

        for strategy in sorted(strategies):
            # Collect data for this strategy
            model_data = []
            for model, stats in self.results[direction].items():
                strategy_stat = next((s for s in stats if s['strategy'] == strategy), None)
                if strategy_stat:
                    full_model_name = model_mapping.get(model, model)
                    model_data.append({
                        'model': full_model_name,
                        'success_rate': strategy_stat['success_rate'],
                        'test_pass_rate': strategy_stat['test_pass_rate']
                    })

            # Prepare data for plotting
            models = [stat['model'] for stat in model_data]
            success_rates = [stat['success_rate'] for stat in model_data]
            test_rates = [stat['test_pass_rate'] for stat in model_data]

            # Create figure and axis
            plt.figure(figsize=(10, 6), facecolor='none')

            # Set width of bars and positions of bars
            width = 0.35
            x = np.arange(len(models))

            # Set y-axis range from 0 to 100
            plt.ylim(0, 100)

            # Create bars
            plt.bar(x - width / 2, success_rates, width, label='Success Rate', color='black')
            plt.bar(x + width / 2, test_rates, width, label='Test Pass Rate', color='lightgrey')

            # Customize the plot
            plt.xlabel('Large Language Models', fontfamily='Arial', weight='bold')
            plt.ylabel('Rate (%)', fontfamily='Arial', weight='bold')
            plt.title(f'{strategy} Performance - {direction.replace("_", " ").title()}',
                      fontfamily='Arial', weight='bold', pad=15)
            plt.xticks(x, models, ha='center', fontfamily='Arial')
            plt.yticks(fontfamily='Arial')
            plt.legend(prop={'family': 'Arial', 'weight': 'bold'})

            # Add value labels on top of bars
            for i, v in enumerate(success_rates):
                plt.text(i - width / 2, v + 0.25, f'{v:.1f}%', ha='center', va='bottom')
            for i, v in enumerate(test_rates):
                plt.text(i + width / 2, v + 0.25, f'{v:.1f}%', ha='center', va='bottom')

            # Adjust layout and save
            plt.tight_layout()
            plt.savefig(os.path.join(report_dir, f'{direction}_{strategy}_model_performance.png'), transparent=True)
            plt.close()


def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(src_dir)
    report_dir = os.path.join(project_dir, 'report')
    os.makedirs(report_dir, exist_ok=True)

    analyzer = RankingAnalysis()

    # Analyze both directions
    for direction in ['java_to_python', 'python_to_java']:
        results_dir = os.path.join(project_dir, direction)
        analyzer.analyze_results(results_dir)

    # Generate and save rankings report
    report = analyzer.generate_rankings()
    report_path = os.path.join(report_dir, 'strategy_rankings.txt')

    with open(report_path, 'w') as f:
        f.write(report)

    print(f"Rankings analysis complete. Report saved to '{report_path}'")

    # Create visualizations
    analyzer.create_visualization(report_dir)
    print(f"Visualization charts saved in '{report_dir}'")

if __name__ == "__main__":
    main()