import os
import re
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

import numpy as np
from matplotlib import pyplot as plt
from prettytable import PrettyTable


class RankingAnalysis:
    def __init__(self):
        self.results = defaultdict(lambda: defaultdict(list))
        self.collaboration_results = defaultdict(lambda: defaultdict(list))
        self.model_mapping = {
            "Mistral": "Codestral-2501",
            "OpenAI": "GPT-4o-mini",
            "Claude": "Claude 3.5 Haiku",
            "Gemini": "Gemini 2.0 Flash",
            "DeepSeek": "DeepSeek-V3"
        }
        self.llm_names = ['Claude', 'DeepSeek', 'OpenAI', 'Mistral', 'Gemini']

    def _get_direction_from_path(self, results_dir: str) -> str:
        """Extract direction from results directory path"""
        try:
            direction = os.path.basename(os.path.normpath(results_dir))
            return direction if '_to_' in direction else "unknown"
        except Exception:
            return "unknown"

    def _calculate_rates(self, filepath: str) -> Tuple[float, float]:
        """Calculate success and test pass rates from results file"""
        total = successful_compilations = 0
        tests_passed_count = total_tests_count = 0

        with open(filepath, 'r') as f:
            content = f.read()
            problems = content.split('Problem ')
            problems = [p for p in problems if p.strip() and ':' in p]
            total = len(problems)

            for problem in problems:
                if "LLMGeneratedTests" in filepath:
                    test_pattern = r"Tests passed: (\d+)/(\d+)"
                    matches = re.search(test_pattern, problem)
                    if matches:
                        passed = int(matches.group(1))
                        total_tests = int(matches.group(2))
                        tests_passed_count += passed
                        total_tests_count += total_tests
                else:
                    if 'Tests passed: True' in problem:
                        tests_passed_count += 1
                    total_tests_count += 1
                if 'Compilation successful: True' in problem:
                    successful_compilations += 1

        success_rate = (successful_compilations / total) * 100 if total > 0 else 0
        test_pass_rate = (tests_passed_count / total_tests_count) * 100 if total > 0 else 0

        return success_rate, test_pass_rate

    def _clean_strategy_name(self, strategy_name: str) -> str:
        """Clean up strategy names for display purposes"""
        if strategy_name.endswith('LLMGeneratedTests'):
            return strategy_name.replace('WithLLMGeneratedTests', ' (LLM)')
        elif strategy_name.endswith('ProvidedTests'):
            return strategy_name.replace('WithProvidedTests', ' (Dataset)')
        return strategy_name

    def _aggregate_strategy_performance(self, data_source: dict) -> dict:
        """Common method to aggregate strategy performance from any data source"""
        strategy_performance = defaultdict(lambda: {'total_success': 0, 'total_test_pass': 0, 'count': 0})

        for direction_data in data_source.values():
            for model_data in direction_data.values():
                for result in model_data:
                    strategy = result['strategy']
                    strategy_performance[strategy]['total_success'] += result['success_rate']
                    strategy_performance[strategy]['total_test_pass'] += result['test_pass_rate']
                    strategy_performance[strategy]['count'] += 1

        return strategy_performance

    def _create_performance_chart(self, strategies: list, success_rates: list, test_rates: list,
                                  title: str, filename: str, report_dir: str, figsize: tuple = (15, 8)):
        """Common method to create stacked bar charts"""
        plt.figure(figsize=figsize)
        x = np.arange(len(strategies))

        plt.bar(x, success_rates, label='Compile Success Rate', color='black')
        plt.bar(x, test_rates, bottom=success_rates, label='Test Pass Rate', color='lightgrey')

        plt.ylim(0, 200)
        plt.xlabel('Prompting Strategies' if 'Strategy' in title else 'Large Language Models',
                   fontfamily='Arial', weight='bold')
        plt.ylabel('Rate (%)', fontfamily='Arial', weight='bold')
        plt.title(title, fontfamily='Arial', weight='bold', pad=15)
        plt.xticks(x, strategies, ha='center', fontfamily='Arial')
        plt.yticks(fontfamily='Arial')
        plt.legend(prop={'family': 'Arial', 'weight': 'bold'})

        # Add value labels on bars
        for i, (success, test) in enumerate(zip(success_rates, test_rates)):
            plt.text(i, success / 2, f'{success:.1f}%', ha='center', va='center',
                     fontweight='bold', color='white', fontfamily='Arial')
            plt.text(i, success + test / 2, f'{test:.1f}%', ha='center', va='center',
                     fontweight='bold', color='black', fontfamily='Arial')

        plt.tight_layout()
        plt.savefig(os.path.join(report_dir, filename))
        plt.close()

    def _create_ranking_table(self, data: list, headers: list) -> PrettyTable:
        """Create a ranking table with common formatting"""
        table = PrettyTable()
        table.field_names = headers

        for rank, item in enumerate(data, 1):
            row = [rank] + [item.get(key, '') for key in headers[1:]]
            table.add_row(row)

        return table

    def analyze_results(self, results_dir: str) -> None:
        direction = self._get_direction_from_path(results_dir)

        for filename in os.listdir(results_dir):
            if filename.endswith('.txt'):
                llm_count = sum(1 for llm in self.llm_names if llm in filename)

                if llm_count > 1:  # Skip collaboration files
                    continue

                strategy_name = filename.split('_')[0]
                model_name = filename.split('_')[1].replace('.txt', '')

                filepath = os.path.join(results_dir, filename)
                success_rate, test_pass_rate = self._calculate_rates(filepath)

                self.results[direction][model_name].append({
                    'strategy': strategy_name,
                    'success_rate': success_rate,
                    'test_pass_rate': test_pass_rate
                })

    def analyze_collaboration_results(self, results_dir: str) -> None:
        """Analyze results from LLM collaboration where filename contains two LLM names"""
        direction = self._get_direction_from_path(results_dir)

        for filename in os.listdir(results_dir):
            if filename.endswith('.txt'):
                llm_count = sum(1 for llm in self.llm_names if llm in filename)

                if llm_count == 2:  # Only process collaboration files
                    parts = filename.replace('.txt', '').split('_')
                    strategy_name = parts[0]

                    found_llms = [llm for llm in self.llm_names if llm in filename]
                    if len(found_llms) == 2:
                        translation_llm, test_generation_llm = found_llms[0], found_llms[1]
                        collaboration_key = f"{translation_llm}+{test_generation_llm}"

                        filepath = os.path.join(results_dir, filename)
                        success_rate, test_pass_rate = self._calculate_rates(filepath)

                        self.collaboration_results[direction][collaboration_key].append({
                            'strategy': strategy_name,
                            'translation_llm': translation_llm,
                            'test_generation_llm': test_generation_llm,
                            'success_rate': success_rate,
                            'test_pass_rate': test_pass_rate
                        })

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
                'strategy': self._clean_strategy_name(strategy),
                'success_rate': stats['success_total'] / stats['count'],
                'test_pass_rate': stats['test_total'] / stats['count']
            }
            for strategy, stats in strategy_stats.items()
        ]

    def generate_rankings(self) -> str:
        report = "Strategy Rankings Report\n"
        report += "=====================\n\n"

        report += "Strategy Rankings By Direction\n"
        report += "==========================\n\n"

        for direction in self.results.keys():
            direction_stats = self._calculate_direction_stats(direction)
            report += f"{direction.replace('_', ' ').title()} Strategy Rankings\n"
            report += "=" * 40 + "\n"
            report += self._create_strategy_ranking_table(f"{direction.replace('_', ' ').title()}", direction_stats)
            report += "\n"

        report += "Detailed Strategy Performance By Direction\n"
        report += "=====================================\n\n"

        for direction in self.results.keys():
            report += f"\n{direction.replace('_', ' ').title()} Strategy Details\n"
            report += "=" * 40 + "\n\n"

            strategies = set()
            for model_stats in self.results[direction].values():
                strategies.update(stat['strategy'] for stat in model_stats)

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

    def _create_strategy_ranking_table(self, title: str, stats: List[Dict]) -> str:
        sorted_stats = sorted(stats, key=lambda x: (x['success_rate'], x['test_pass_rate']), reverse=True)

        table = self._create_ranking_table(sorted_stats,
                                           ["Rank", "Strategy", "Compile Success Rate", "Test Passed Rate"])

        for i, stat in enumerate(sorted_stats):
            table._rows[i] = [i + 1, stat['strategy'], f"{stat['success_rate']:.2f}%", f"{stat['test_pass_rate']:.2f}%"]

        return f"\n{title}\n{'-' * len(title)}\n{table}\n\n"

    def _create_model_performance_table(self, strategy: str, stats: List[Dict]) -> str:
        sorted_stats = sorted(stats, key=lambda x: (x['success_rate'], x['test_pass_rate']), reverse=True)

        table = self._create_ranking_table(sorted_stats,
                                           ["Rank", "Model", "Compile Success Rate", "Test Passed Rate"])

        for i, stat in enumerate(sorted_stats):
            table._rows[i] = [i + 1, stat['model'], f"{stat['success_rate']:.2f}%", f"{stat['test_pass_rate']:.2f}%"]

        return f"\n{strategy} Performance\n{'-' * len(strategy + ' Performance')}\n{table}\n\n"

    def create_visualization(self, report_dir: str) -> None:
        for direction in self.results.keys():
            stats = self._calculate_direction_stats(direction)
            strategies = [stat['strategy'] for stat in stats]
            success_rates = [stat['success_rate'] for stat in stats]
            test_rates = [stat['test_pass_rate'] for stat in stats]

            self._create_performance_chart(
                strategies, success_rates, test_rates,
                f'Strategy Performance - {direction.replace("_", " ").title()}',
                f'strategy_performance_{direction}.png',
                report_dir
            )

            self._create_model_performance_charts(direction, report_dir)

    def _create_model_performance_charts(self, direction: str, report_dir: str) -> None:
        strategies = set()
        for model_stats in self.results[direction].values():
            strategies.update(stat['strategy'] for stat in model_stats)

        for strategy in sorted(strategies):
            model_data = []
            for model, stats in self.results[direction].items():
                strategy_stat = next((s for s in stats if s['strategy'] == strategy), None)
                if strategy_stat:
                    full_model_name = self.model_mapping.get(model, model)
                    model_data.append({
                        'model': full_model_name,
                        'success_rate': strategy_stat['success_rate'],
                        'test_pass_rate': strategy_stat['test_pass_rate']
                    })

            models = [stat['model'] for stat in model_data]
            success_rates = [stat['success_rate'] for stat in model_data]
            test_rates = [stat['test_pass_rate'] for stat in model_data]

            self._create_performance_chart(
                models, success_rates, test_rates,
                f'{strategy} Performance - {direction.replace("_", " ").title()}',
                f'{direction}_{strategy}_model_performance.png',
                report_dir, figsize=(10, 6)
            )

    def generate_collaboration_report(self) -> str:
        """Generate a report comparing LLM collaboration performance"""
        if not self.collaboration_results:
            return "No collaboration results found.\n"

        report = "LLM Collaboration Analysis Report\n"
        report += "================================\n\n"

        for direction in self.collaboration_results.keys():
            report += f"{direction.replace('_', ' ').title()} Collaboration Results\n"
            report += "=" * 50 + "\n\n"

            collaboration_stats = defaultdict(lambda: {'success_total': 0, 'test_total': 0, 'count': 0})

            for collab_pair, results in self.collaboration_results[direction].items():
                for result in results:
                    collaboration_stats[collab_pair]['success_total'] += result['success_rate']
                    collaboration_stats[collab_pair]['test_total'] += result['test_pass_rate']
                    collaboration_stats[collab_pair]['count'] += 1

            # Create ranking table
            table = PrettyTable()
            table.field_names = ["Rank", "Translation LLM", "Test Generation LLM", "Avg Compile Success",
                                 "Avg Test Pass"]

            collab_performance = []
            for collab_pair, stats in collaboration_stats.items():
                translation_llm, test_gen_llm = collab_pair.split('+')
                avg_success = stats['success_total'] / stats['count']
                avg_test = stats['test_total'] / stats['count']
                collab_performance.append({
                    'pair': collab_pair,
                    'translation_llm': translation_llm,
                    'test_gen_llm': test_gen_llm,
                    'avg_success': avg_success,
                    'avg_test': avg_test
                })

            collab_performance.sort(key=lambda x: (x['avg_success'], x['avg_test']), reverse=True)

            for rank, perf in enumerate(collab_performance, 1):
                table.add_row([
                    rank,
                    perf['translation_llm'],
                    perf['test_gen_llm'],
                    f"{perf['avg_success']:.2f}%",
                    f"{perf['avg_test']:.2f}%"
                ])

            report += str(table) + "\n\n"

            # Strategy-wise collaboration performance
            report += f"Strategy-wise Collaboration Performance for {direction.replace('_', ' ').title()}\n"
            report += "-" * 60 + "\n\n"

            strategies = set()
            for results in self.collaboration_results[direction].values():
                strategies.update(result['strategy'] for result in results)

            for strategy in sorted(strategies):
                clean_strategy = self._clean_strategy_name(strategy)
                report += f"{clean_strategy} Strategy\n"
                report += "~" * len(clean_strategy + " Strategy") + "\n"

                strategy_table = PrettyTable()
                strategy_table.field_names = ["Translation LLM", "Test Generation LLM", "Compile Success", "Test Pass"]

                for collab_pair, results in self.collaboration_results[direction].items():
                    strategy_result = next((r for r in results if r['strategy'] == strategy), None)
                    if strategy_result:
                        translation_llm, test_gen_llm = collab_pair.split('+')
                        strategy_table.add_row([
                            translation_llm,
                            test_gen_llm,
                            f"{strategy_result['success_rate']:.2f}%",
                            f"{strategy_result['test_pass_rate']:.2f}%"
                        ])

                report += str(strategy_table) + "\n\n"

        return report

    def create_collaboration_visualization(self, report_dir: str) -> None:
        """Create visualizations for LLM collaboration performance"""
        if not self.collaboration_results:
            return

        for direction in self.collaboration_results.keys():
            collaboration_stats = defaultdict(lambda: {'success_total': 0, 'test_total': 0, 'count': 0})

            for collab_pair, results in self.collaboration_results[direction].items():
                for result in results:
                    collaboration_stats[collab_pair]['success_total'] += result['success_rate']
                    collaboration_stats[collab_pair]['test_total'] += result['test_pass_rate']
                    collaboration_stats[collab_pair]['count'] += 1

            pairs = []
            success_rates = []
            test_rates = []

            for collab_pair, stats in collaboration_stats.items():
                translation_llm, test_gen_llm = collab_pair.split('+')
                pair_label = f"{translation_llm}\n+\n{test_gen_llm}"
                pairs.append(pair_label)
                success_rates.append(stats['success_total'] / stats['count'])
                test_rates.append(stats['test_total'] / stats['count'])

            self._create_performance_chart(
                pairs, success_rates, test_rates,
                f'LLM Collaboration Performance - {direction.replace("_", " ").title()}',
                f'collaboration_performance_{direction}.png',
                report_dir, figsize=(14, 8)
            )

    def create_collaboration_heatmap(self, report_dir: str) -> None:
        """Create heatmap visualization for LLM collaboration performance"""
        if not self.collaboration_results:
            return

        for direction in self.collaboration_results.keys():
            collaboration_stats = defaultdict(lambda: {'success_total': 0, 'test_total': 0, 'count': 0})

            for collab_pair, results in self.collaboration_results[direction].items():
                for result in results:
                    collaboration_stats[collab_pair]['success_total'] += result['success_rate']
                    collaboration_stats[collab_pair]['test_total'] += result['test_pass_rate']
                    collaboration_stats[collab_pair]['count'] += 1

            translation_llms = set()
            test_gen_llms = set()

            for collab_pair in collaboration_stats.keys():
                trans_llm, test_llm = collab_pair.split('+')
                translation_llms.add(trans_llm)
                test_gen_llms.add(test_llm)

            translation_llms = sorted(translation_llms)
            test_gen_llms = sorted(test_gen_llms)

            success_matrix = np.zeros((len(translation_llms), len(test_gen_llms)))
            test_matrix = np.zeros((len(translation_llms), len(test_gen_llms)))

            for i, trans_llm in enumerate(translation_llms):
                for j, test_llm in enumerate(test_gen_llms):
                    collab_key = f"{trans_llm}+{test_llm}"
                    if collab_key in collaboration_stats:
                        stats = collaboration_stats[collab_key]
                        success_matrix[i, j] = stats['success_total'] / stats['count']
                        test_matrix[i, j] = stats['test_total'] / stats['count']

            self._create_heatmap_subplot(success_matrix, test_matrix, translation_llms, test_gen_llms,
                                         direction, report_dir)

    def _create_heatmap_subplot(self, success_matrix: np.ndarray, test_matrix: np.ndarray,
                                translation_llms: list, test_gen_llms: list, direction: str, report_dir: str):
        """Create heatmap subplots for success and test matrices"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Success rate heatmap
        im1 = ax1.imshow(success_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        self._configure_heatmap_axes(ax1, translation_llms, test_gen_llms, 'Compile Success Rate (%)')
        self._add_heatmap_annotations(ax1, success_matrix)

        # Test pass rate heatmap
        im2 = ax2.imshow(test_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        self._configure_heatmap_axes(ax2, translation_llms, test_gen_llms, 'Test Pass Rate (%)')
        self._add_heatmap_annotations(ax2, test_matrix)

        plt.colorbar(im1, ax=ax1, shrink=0.8)
        plt.colorbar(im2, ax=ax2, shrink=0.8)

        plt.suptitle(f'LLM Collaboration Performance - {direction.replace("_", " ").title()}',
                     fontfamily='Arial', weight='bold', fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(report_dir, f'collaboration_heatmap_{direction}.png'))
        plt.close()

    def _configure_heatmap_axes(self, ax, translation_llms: list, test_gen_llms: list, title: str):
        """Configure heatmap axes with common settings"""
        ax.set_xticks(range(len(test_gen_llms)))
        ax.set_yticks(range(len(translation_llms)))
        ax.set_xticklabels(test_gen_llms, fontfamily='Arial')
        ax.set_yticklabels(translation_llms, fontfamily='Arial')
        ax.set_xlabel('Test Generation LLM', fontfamily='Arial', weight='bold')
        ax.set_ylabel('Translation LLM', fontfamily='Arial', weight='bold')
        ax.set_title(title, fontfamily='Arial', weight='bold')

    def _add_heatmap_annotations(self, ax, matrix: np.ndarray):
        """Add text annotations to heatmap"""
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                ax.text(j, i, f'{matrix[i, j]:.1f}%', ha="center", va="center",
                        color="black", fontweight='bold')

    def analyze_overall_strategy_performance(self):
        """Analyze overall strategy performance across all language pairs and models"""
        strategy_performance = self._aggregate_strategy_performance(self.results)

        overall_results = {}
        for strategy, data in strategy_performance.items():
            if data['count'] > 0:
                overall_results[strategy] = {
                    'avg_success_rate': data['total_success'] / data['count'],
                    'avg_test_pass_rate': data['total_test_pass'] / data['count'],
                    'total_experiments': data['count']
                }

        sorted_strategies = sorted(overall_results.items(),
                                   key=lambda x: x[1]['avg_success_rate'],
                                   reverse=True)

        # for strategy, metrics in sorted_strategies:
        #     print(f"{strategy:<20} {metrics['avg_success_rate']:<15.1f} "
        #           f"{metrics['avg_test_pass_rate']:<18.1f} {metrics['total_experiments']:<12}")

        return overall_results

    def create_overall_strategy_visualization(self, report_dir: str) -> None:
        """Create visualization for overall strategy performance across all language pairs"""
        strategy_performance = self._aggregate_strategy_performance(self.results)

        strategies = []
        success_rates = []
        test_rates = []

        for strategy, data in strategy_performance.items():
            if data['count'] > 0:
                strategies.append(self._clean_strategy_name(strategy))
                success_rates.append(data['total_success'] / data['count'])
                test_rates.append(data['total_test_pass'] / data['count'])

        # Sort by success rate
        sorted_data = sorted(zip(strategies, success_rates, test_rates),
                             key=lambda x: x[1], reverse=True)
        strategies, success_rates, test_rates = zip(*sorted_data)

        self._create_performance_chart(
            strategies, success_rates, test_rates,
            'Overall Strategy Performance (All Language Pairs)',
            'overall_strategy_performance.png',
            report_dir
        )

    def analyze_strategy_performance_by_llm(self):
        """Analyze strategy performance for each individual LLM across all language pairs"""
        # print("\n" + "=" * 100)
        # print("STRATEGY PERFORMANCE BY LLM (All Language Pairs)")
        # print("=" * 100)

        all_llms = set()
        for direction_data in self.results.values():
            all_llms.update(direction_data.keys())

        for llm in sorted(all_llms):
            strategy_performance = defaultdict(lambda: {'total_success': 0, 'total_test_pass': 0, 'count': 0})

            for direction_data in self.results.values():
                if llm in direction_data:
                    for result in direction_data[llm]:
                        strategy = result['strategy']
                        strategy_performance[strategy]['total_success'] += result['success_rate']
                        strategy_performance[strategy]['total_test_pass'] += result['test_pass_rate']
                        strategy_performance[strategy]['count'] += 1

            llm_results = {}
            for strategy, data in strategy_performance.items():
                if data['count'] > 0:
                    llm_results[strategy] = {
                        'avg_success_rate': data['total_success'] / data['count'],
                        'avg_test_pass_rate': data['total_test_pass'] / data['count'],
                        'total_experiments': data['count']
                    }

            sorted_strategies = sorted(llm_results.items(),
                                       key=lambda x: x[1]['avg_success_rate'],
                                       reverse=True)

            # print(f"\n{llm}")
            # print("-" * 80)
            # print(f"{'Strategy':<25} {'Avg Success %':<15} {'Avg Test Pass %':<18} {'Experiments':<12}")
            # print("-" * 80)

            for strategy, metrics in sorted_strategies:
                clean_strategy = self._clean_strategy_name(strategy)
                # print(f"{clean_strategy:<25} {metrics['avg_success_rate']:<15.1f} "
                #       f"{metrics['avg_test_pass_rate']:<18.1f} {metrics['total_experiments']:<12}")

        return True

    def create_strategy_performance_by_llm_visualization(self, report_dir: str) -> None:
        """Create bar charts showing strategy performance for each LLM across all language pairs"""
        all_llms = set()
        for direction_data in self.results.values():
            all_llms.update(direction_data.keys())

        for llm in sorted(all_llms):
            strategy_performance = defaultdict(lambda: {'total_success': 0, 'total_test_pass': 0, 'count': 0})

            for direction_data in self.results.values():
                if llm in direction_data:
                    for result in direction_data[llm]:
                        strategy = result['strategy']
                        strategy_performance[strategy]['total_success'] += result['success_rate']
                        strategy_performance[strategy]['total_test_pass'] += result['test_pass_rate']
                        strategy_performance[strategy]['count'] += 1

            strategies = []
            success_rates = []
            test_rates = []

            for strategy, data in strategy_performance.items():
                if data['count'] > 0:
                    strategies.append(self._clean_strategy_name(strategy))
                    success_rates.append(data['total_success'] / data['count'])
                    test_rates.append(data['total_test_pass'] / data['count'])

            sorted_data = sorted(zip(strategies, success_rates, test_rates),
                                 key=lambda x: x[1], reverse=True)
            strategies, success_rates, test_rates = zip(*sorted_data)

            self._create_performance_chart(
                strategies, success_rates, test_rates,
                f'Strategy Performance - {llm} (All Language Pairs)',
                f'strategy_performance_by_llm_{llm}.png',
                report_dir
            )


def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(src_dir)
    report_dir = os.path.join(project_dir, 'report')
    os.makedirs(report_dir, exist_ok=True)

    analyzer = RankingAnalysis()

    # Analyze both directions
    for direction in ['python_to_javascript', 'python_to_java', 'javascript_to_python',
                      'javascript_to_java', 'java_to_python', 'java_to_javascript']:
        results_dir = os.path.join(project_dir, direction)
        analyzer.analyze_results(results_dir)
        analyzer.analyze_collaboration_results(results_dir)
        analyzer.analyze_overall_strategy_performance()
        analyzer.analyze_strategy_performance_by_llm()

    # Generate and save rankings report
    report = analyzer.generate_rankings()
    collaboration_report = analyzer.generate_collaboration_report()

    full_report = report + "\n" + collaboration_report

    report_path = os.path.join(report_dir, 'strategy_rankings.txt')

    with open(report_path, 'w') as f:
        f.write(full_report)

    print(f"Rankings analysis complete. Report saved to '{report_path}'")

    # Create visualizations
    analyzer.create_visualization(report_dir)
    analyzer.create_collaboration_visualization(report_dir)
    analyzer.create_collaboration_heatmap(report_dir)
    analyzer.create_overall_strategy_visualization(report_dir)
    analyzer.create_strategy_performance_by_llm_visualization(report_dir)
    print(f"Visualization charts saved in '{report_dir}'")


if __name__ == "__main__":
    main()