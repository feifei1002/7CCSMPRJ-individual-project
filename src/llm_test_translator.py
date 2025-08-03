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
        if self.num_tests != 5:
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
