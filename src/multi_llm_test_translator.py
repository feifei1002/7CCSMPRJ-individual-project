import os
from typing import List, Type

from src.code_translator import CodeTranslator
from src.data_utils import get_file_extension


class MultiLLMTestTranslator(CodeTranslator):
    def __init__(self, source_lang: str, target_lang: str,
                 translation_llms: dict, test_generation_llms: dict,
                 prompt_strategies: List[Type], test_gen_prompts: dict, num_tests=5):
        super().__init__(source_lang, target_lang, translation_llms, prompt_strategies)
        self.test_generation_llms = test_generation_llms
        self.test_gen_prompts = test_gen_prompts
        self.num_tests = num_tests

    def get_output_paths(self, translation_llm_name: str, test_gen_llm_name: str, strategy_name: str) -> tuple:
        output_dir, results_file = self.get_base_output_paths(f"{translation_llm_name}_{test_gen_llm_name}", strategy_name)
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
        for translation_llm_name, translation_llm in self.llm_models.items():
            for test_gen_llm_name, test_gen_llm in self.test_generation_llms.items():
                for strategy in self.prompt_strategies:
                    output_dir, results_file, file_path = self.get_output_paths(
                        translation_llm_name, test_gen_llm_name, strategy.__name__
                    )

                    self._process_translation_task(
                        translation_llm_name, translation_llm,
                        test_gen_llm_name, test_gen_llm, strategy,
                        output_dir, results_file, file_path
                    )

                    # for index, (source, target) in enumerate(zip(self.code_dataset, self.test_dataset)):
                    #     source_declaration = source.get("declaration")
                    #     source_code = source.get("canonical_solution")
                    #     target_declaration = target.get("declaration")
                    #
                    #     # Generate test cases using test generation LLM
                    #     test_gen_context = {"code": source_code}
                    #     test_gen_prompt = self.test_gen_prompts[self.source_language]
                    #     test_gen_messages = test_gen_prompt.prompt(test_gen_context, num_tests=self.num_tests)
                    #     generated_tests = test_gen_llm.generate(test_gen_messages)
                    #
                    #     # Translate using translation LLM
                    #     context = {
                    #         "source_language": self.source_language,
                    #         "target_language": self.target_language,
                    #         "source_declaration": source_declaration,
                    #         "code": source_code,
                    #         "target_declaration": target_declaration,
                    #         "test_cases": generated_tests,
                    #         "source_language_lower": self.source_language.lower(),
                    #         "target_language_lower": self.target_language.lower(),
                    #     }
                    #
                    #     prompt_messages = strategy.prompt(context)
                    #     translated_code = translation_llm.generate(prompt_messages)
                    #
                    #     self.write_code_and_tests(output_dir, translated_code, generated_tests)
                    #
                    #     compilation_success, tests_passed, compilation_error, test_error, test_stats = self.execute_and_evaluate(file_path, index)
                    #     self.write_results(results_file, index, compilation_success, tests_passed,
                    #                        compilation_error, test_error, test_stats)
                    #     print(f"Processed problem {index} using {translation_llm_name} for translation "
                    #           f"and {test_gen_llm_name} for test generation")