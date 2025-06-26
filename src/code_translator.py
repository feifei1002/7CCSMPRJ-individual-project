import os
import re
import traceback
from typing import List, Type

from src.code_execution import execute_code_and_tests
from src.config import PROJECT_DIR
from src.data_utils import load_test_dataset, load_code_dataset, get_file_extension


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

    @staticmethod
    def get_class_name(code: str) -> str:
        """Extract the main class name from Java code"""
        match = re.search(r'public\s+class\s+(\w+)', code)
        if match:
            return match.group(1)
        match = re.search(r'class\s+(\w+)', code)
        return match.group(1) if match else "Solution"

    @staticmethod
    def get_test_class_name(test_code: str) -> str:
        match = re.search(r'class\s+(\w+)', test_code)
        if match:
            return match.group(1)
        raise ValueError("Could not find class name in test code")

    def extract_marked_sections(self, text: str) -> tuple:
        test_match = re.search(r'TEST_BEGIN\n(.*?)\nTEST_END', text, re.DOTALL)
        test_code = test_match.group(1).strip() if test_match else ""

        code_match = re.search(r'CODE_BEGIN\n(.*?)\nCODE_END', text, re.DOTALL)
        solution_code = code_match.group(1).strip() if code_match else ""

        return solution_code, test_code

    def write_code_and_tests(self, output_dir: str, translated_code: str, source_tests: str, is_dataset: bool = False) -> None:

        if is_dataset:
            file_extension = get_file_extension(self.target_language)
            file_path = os.path.join(output_dir, "Main.java" if self.target_language == "Java" else f"main.{file_extension}")
            with open(file_path, "w") as f:
                f.write(translated_code + "\n")
                if source_tests:
                    f.write(source_tests)
            return

        solution_code, translated_tests = self.extract_marked_sections(translated_code)
        clean_tests = self.clean_code(translated_tests)

        if self.target_language == "Java":
            class_name = self.get_class_name(solution_code)
            solution_path = os.path.join(output_dir, f"{class_name}.java")
            test_class_name = self.get_test_class_name(clean_tests)
            test_path = os.path.join(output_dir, f"{test_class_name}.java")
        else:
            solution_path = os.path.join(output_dir, f"solution.{get_file_extension(self.target_language)}")
            test_path = os.path.join(output_dir, f"test_cases.{get_file_extension(self.target_language)}")

        with open(solution_path, "w") as f:
            f.write(solution_code)
        with open(test_path, "w") as f:
            f.write(clean_tests)

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
                test_error = test_error.encode("ascii", "replace").decode("ascii")
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