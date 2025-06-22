from src.llms import DeepseekLLM
from src.prompts import (
    InitialPromptWithProvidedTests,
    TestFirstPromptWithProvidedTests,
    StepByStepPromptWithProvidedTests
)
from src.llm_prompts import (
    InitialPromptWithLLMGeneratedTests,
    TestFirstPromptWithLLMGeneratedTests,
    StepByStepPromptWithLLMGeneratedTests
)
from src.tests_prompts import GenerateTestCasesPromptPython, GenerateTestCasesPromptJava
from src.dataset_translator import DatasetTestTranslator
from src.llm_test_translator import LLMTestTranslator


def run_dataset_translation():
    llm_models = {
        # "Mistral": MistralLLM(),
        # "OpenAI": OpenAILLM(),
        # "Claude": ClaudeLLM(),
        # "Gemini": GeminiLLM(),
        "DeepSeek": DeepseekLLM()
    }
    prompt_strategies = [
        InitialPromptWithProvidedTests,
        # TestFirstPromptWithProvidedTests,
        # StepByStepPromptWithProvidedTests
    ]

    translator = DatasetTestTranslator("Python", "Java", llm_models, prompt_strategies)
    translator.translate()


def run_llm_test_translation():
    llm_models = {
        # "Mistral": MistralLLM(),
        # "OpenAI": OpenAILLM(),
        # "Claude": ClaudeLLM(),
        # "Gemini": GeminiLLM(),
        "DeepSeek": DeepseekLLM()
    }
    prompt_strategies = [
        InitialPromptWithLLMGeneratedTests,
        # TestFirstPromptWithLLMGeneratedTests,
        # StepByStepPromptWithLLMGeneratedTests
    ]
    test_gen_prompts = {
        "Python": GenerateTestCasesPromptPython,
        "Java": GenerateTestCasesPromptJava
    }

    translator = LLMTestTranslator("Python", "Java", llm_models, prompt_strategies, test_gen_prompts)
    translator.translate()


def main():
    # print("Starting translation with dataset-provided tests...")
    # run_dataset_translation()

    print("\nStarting translation with LLM-generated tests...")
    run_llm_test_translation()


if __name__ == "__main__":
    main()