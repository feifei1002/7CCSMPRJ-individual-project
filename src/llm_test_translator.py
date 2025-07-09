import os
from typing import List, Type

from src.code_translator import CodeTranslator
from src.data_utils import get_file_extension


class LLMTestTranslator(CodeTranslator):
    def __init__(self, source_lang: str, target_lang: str, llm_models: dict,
                 prompt_strategies: List[Type], test_gen_prompts: dict, num_tests=5):
        super().__init__(source_lang, target_lang, llm_models, prompt_strategies)
        self.test_gen_prompts = test_gen_prompts
        self.num_tests = num_tests

    def get_output_paths(self, llm_name: str, strategy_name: str) -> tuple:
        output_dir, results_file = self.get_base_output_paths(llm_name, strategy_name)
        if self.num_tests > 5:
            results_file = results_file.replace('.txt', f'_{self.num_tests}.txt')
        if self.target_language == "Java":
            first_code = self.code_dataset[0]["canonical_solution"]
            class_name = self.get_class_name(first_code)
            file_path = os.path.join(output_dir, f"{class_name}.java")
        else:
            file_path = os.path.join(output_dir, f"solution.{get_file_extension(self.target_language)}")
        return output_dir, results_file, file_path

    def translate(self):
        for llm_name, llm in self.llm_models.items():
            for strategy in self.prompt_strategies:
                output_dir, results_file, file_path = self.get_output_paths(llm_name, strategy.__name__)


                self._process_translation_task(
                    llm_name, llm, llm_name, llm, strategy, output_dir, results_file, file_path
                )
                # for index, (source, target) in enumerate(zip(self.code_dataset, self.test_dataset)):
                #     try:
                #         source_declaration = source.get("declaration")
                #         source_code = source.get("canonical_solution")
                #         target_declaration = target.get("declaration")
                #
                #         # Generate test cases
                #         test_gen_context = {"code": source_code}
                #         test_gen_prompt = self.test_gen_prompts[self.source_language]
                #         test_gen_messages = test_gen_prompt.prompt(test_gen_context, num_tests=self.num_tests)
                #         generated_tests = llm.generate(test_gen_messages)
                #
                #         # Prepare context for translation
                #         context = {
                #             "source_language": self.source_language,
                #             "target_language": self.target_language,
                #             "source_declaration": source_declaration,
                #             "code": source_code,
                #             "target_declaration": target_declaration,
                #             "test_cases": generated_tests,
                #             "source_language_lower": self.source_language.lower(),
                #             "target_language_lower": self.target_language.lower(),
                #         }
                #
                #         prompt_messages = strategy.prompt(context)
                #         translated_code = llm.generate(prompt_messages)
                #
                #         self.write_code_and_tests(output_dir, translated_code, generated_tests)
                #
                #         compilation_success, tests_passed, compilation_error, test_error, test_stats = self.execute_and_evaluate(file_path, index)
                #         self.write_results(results_file, index, compilation_success, tests_passed, compilation_error, test_error, test_stats)
                #         print(f"Processed problem {index}")
                #     except ValueError as e:
                #         print(
                #             f"Could not process problem {index} with {llm_name} using {strategy.__name__}. Error: {e}")