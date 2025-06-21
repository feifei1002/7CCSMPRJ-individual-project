import os
import re
from typing import List, Type

from src.code_translator import CodeTranslator


class LLMTestTranslator(CodeTranslator):
    def __init__(self, source_lang: str, target_lang: str, llm_models: dict,
                 prompt_strategies: List[Type], test_gen_prompts: dict):
        super().__init__(source_lang, target_lang, llm_models, prompt_strategies)
        self.test_gen_prompts = test_gen_prompts

    def get_output_paths(self, llm_name: str, strategy_name: str) -> tuple:
        output_dir, results_file = self.get_base_output_paths(llm_name, strategy_name)
        # Return the solution.py path as the file_path for execution
        file_path = os.path.join(output_dir, "solution.py")
        return output_dir, results_file, file_path

    def extract_marked_sections(self, text: str) -> tuple:
        # Extract code between TEST_BEGIN and TEST_END
        test_match = re.search(r'TEST_BEGIN\n(.*?)\nTEST_END', text, re.DOTALL)
        test_code = test_match.group(1).strip() if test_match else ""

        # Extract code between CODE_BEGIN and CODE_END
        code_match = re.search(r'CODE_BEGIN\n(.*?)\nCODE_END', text, re.DOTALL)
        solution_code = code_match.group(1).strip() if code_match else ""

        return solution_code, test_code

    def write_code_and_tests(self, output_dir: str, file_path: str, code: str, tests: str) -> None:
        # Extract marked sections from the code
        solution_code, test_code = self.extract_marked_sections(code)

        # Write solution code to solution.py
        with open(file_path, "w") as f:
            f.write(solution_code)
            # Write tests to test_cases.py
        test_path = os.path.join(output_dir, "test_cases.py")
        with open(test_path, "w") as f:
            f.write(test_code)

    def translate(self):
        for llm_name, llm in self.llm_models.items():
            for strategy in self.prompt_strategies:
                output_dir, results_file, file_path = self.get_output_paths(llm_name, strategy.__name__)

                for index, (code, test) in enumerate(zip(self.code_dataset, self.test_dataset)):
                    source_code = code.get("canonical_solution")
                    declaration = test.get("declaration")

                    # Generate test cases
                    test_gen_context = {"code": source_code}
                    test_gen_prompt = self.test_gen_prompts[self.target_language]
                    test_gen_messages = test_gen_prompt.prompt(test_gen_context)
                    generated_tests = llm.generate(test_gen_messages)

                    context = {
                        "source_language": self.source_language,
                        "target_language": self.target_language,
                        "declaration": declaration,
                        "code": source_code,
                        "test_cases": generated_tests,
                        "source_language_lower": self.source_language.lower(),
                        "target_language_lower": self.target_language.lower(),
                    }

                    prompt_messages = strategy.prompt(context)
                    translated_code = llm.generate(prompt_messages)

                    self.write_code_and_tests(output_dir, file_path, translated_code, generated_tests)

                    compilation_success, tests_passed, compilation_error, test_error, test_stats = self.execute_and_evaluate(file_path, index)
                    self.write_results(results_file, index, compilation_success, tests_passed, compilation_error, test_error, test_stats)
                    print(f"Processed problem {index}")