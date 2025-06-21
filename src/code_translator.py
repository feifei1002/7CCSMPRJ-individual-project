import os
import re
import traceback
from typing import List, Type

from src.code_execution import execute_code_and_tests
from src.config import PROJECT_DIR
from src.data_utils import load_test_dataset, load_code_dataset

class CodeTranslator:
    def __init__(self, source_lang: str, target_lang: str, llm_models: dict, prompt_strategies: List[Type]):
        self.source_language = source_lang
        self.target_language = target_lang
        self.llm_models = llm_models
        self.prompt_strategies = prompt_strategies
        self.test_dataset = load_test_dataset(target_lang)
        self.code_dataset = load_code_dataset(source_lang)

    def clean_code(self, code: str) -> str:
        code = code.strip()
        marker_match = re.search(r'```(?:\w+)?\n(.*?)\n```', code, re.DOTALL)
        if marker_match:
            code = marker_match.group(1).strip()
            code = '\n'.join(line.rstrip() for line in code.splitlines() if line.strip())
            return code
        return code

    def get_base_output_paths(self, llm_name: str, strategy_name: str) -> tuple:
        base_folder = f"{self.source_language.lower()}_to_{self.target_language.lower()}"
        output_dir = os.path.join(os.path.dirname(PROJECT_DIR), base_folder)
        os.makedirs(output_dir, exist_ok=True)
        results_file = os.path.join(output_dir, f"{strategy_name}_{llm_name}.txt")
        return output_dir, results_file

    def write_results(self, results_file: str, index: int, compilation_success: bool,
                      tests_passed: bool, compilation_error: str, test_error: str, test_stats: str = "0/0") -> None:
        with open(results_file, "a") as f:
            f.write(f"Problem {index}:\n")
            f.write(f"Compilation successful: {compilation_success}\n")

            if "LLMGeneratedTests" in results_file:
                f.write(f"Tests passed: {test_stats}\n")
            else:
                f.write(f"Tests passed: {tests_passed}\n")
            if compilation_error:
                f.write(f"Compilation error: {compilation_error}\n")
            if test_error:
                f.write(f"Test error: {test_error}\n")
            f.write("-" * 50 + "\n")

    def execute_and_evaluate(self, file_path: str, index: int) -> tuple:
        try:
            result = execute_code_and_tests(file_path, self.target_language, self.test_dataset, index)
            compilation_success = result.get("compilation_success", False)
            tests_passed = result.get("tests_passed", False)
            compilation_error = result.get("compilation_error", "")
            test_error = result.get("test_error", "")
            test_stats = result.get("test_stats", "0/0")
        except Exception as e:
            compilation_success = False
            tests_passed = False
            compilation_error = f"System error: {str(e)}\n{traceback.format_exc()}"
            test_error = ""
            test_stats = "0/0"
        return compilation_success, tests_passed, compilation_error, test_error, test_stats