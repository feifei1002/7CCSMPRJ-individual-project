import os

from src.code_translator import CodeTranslator
from src.data_utils import get_file_extension


class DatasetTestTranslator(CodeTranslator):
    def get_output_paths(self, llm_name: str, strategy_name: str) -> tuple:
        output_dir, results_file = self.get_base_output_paths(llm_name, strategy_name)
        file_extension = get_file_extension(self.target_language)
        file_path = os.path.join(output_dir, "Main.java" if self.target_language == "Java" else f"main.{file_extension}")
        return output_dir, results_file, file_path


    def translate(self):
        for llm_name, llm in self.llm_models.items():
            for strategy in self.prompt_strategies:
                output_dir, results_file, file_path = self.get_output_paths(llm_name, strategy.__name__)

                for index, (source, target) in enumerate(zip(self.code_dataset, self.test_dataset)):
                    source_declaration = source.get("declaration")
                    source_code = source.get("canonical_solution")
                    target_declaration = target.get("declaration")
                    test_cases = target.get("test")

                    context = {
                        "source_language": self.source_language,
                        "target_language": self.target_language,
                        "source_declaration": source_declaration,
                        "code": source_code,
                        "target_declaration": target_declaration,
                        "test_cases": test_cases,
                        "source_language_lower": self.source_language.lower(),
                        "target_language_lower": self.target_language.lower(),
                    }

                    prompt_messages = strategy.prompt(context)
                    translated_code = llm.generate(prompt_messages)
                    cleaned_code = self.clean_code(translated_code)

                    self.write_code_and_tests(output_dir, cleaned_code, test_cases, is_dataset=True)

                    compilation_success, tests_passed, compilation_error, test_error, test_stats = self.execute_and_evaluate(file_path, index)
                    self.write_results(results_file, index, compilation_success, tests_passed, compilation_error, test_error, test_stats)
                    print(f"Processed problem {index}")