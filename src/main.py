from src.llms import DeepseekLLM, MistralLLM, OpenAILLM, ClaudeLLM, GeminiLLM
from src.multi_llm_test_translator import MultiLLMTestTranslator
from src.prompts import (
    InitialPromptWithProvidedTests,
    TestFirstPromptWithProvidedTests,
    StepByStepPromptWithProvidedTests, NoTestPrompt
)
from src.llm_prompts import (
    InitialPromptWithLLMGeneratedTests,
    TestFirstPromptWithLLMGeneratedTests,
    StepByStepPromptWithLLMGeneratedTests
)
from src.tests_prompts import GenerateTestCasesPromptPython, GenerateTestCasesPromptJava, \
    GenerateTestCasesPromptJavaScript, GenerateTestCasesPromptCPP
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
        NoTestPrompt,
        InitialPromptWithProvidedTests,
        TestFirstPromptWithProvidedTests,
        StepByStepPromptWithProvidedTests
    ]

    translator = DatasetTestTranslator("Java", "JavaScript", llm_models, prompt_strategies)
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
        TestFirstPromptWithLLMGeneratedTests,
        StepByStepPromptWithLLMGeneratedTests
    ]
    test_gen_prompts = {
        "Python": GenerateTestCasesPromptPython,
        "Java": GenerateTestCasesPromptJava,
        "JavaScript": GenerateTestCasesPromptJavaScript,
        # "C++": GenerateTestCasesPromptCPP,
    }

    translator = LLMTestTranslator("Java", "JavaScript", llm_models, prompt_strategies, test_gen_prompts)
    translator.translate()

def run_multi_llm_test_translation():
    translation_llm_models = {
        "Mistral": MistralLLM(),
        # "OpenAI": OpenAILLM(),
        # "Claude": ClaudeLLM(),
        # "Gemini": GeminiLLM(),
        # "DeepSeek": DeepseekLLM()
    }
    test_generation_llm_models = {
        # "Mistral": MistralLLM(),
        # "OpenAI": OpenAILLM(),
        # "Claude": ClaudeLLM(),
        # "Gemini": GeminiLLM(),
        "DeepSeek": DeepseekLLM()
    }
    prompt_strategies = [
        InitialPromptWithLLMGeneratedTests,
        TestFirstPromptWithLLMGeneratedTests,
        StepByStepPromptWithLLMGeneratedTests
    ]
    test_gen_prompts = {
        "Python": GenerateTestCasesPromptPython,
        "Java": GenerateTestCasesPromptJava,
        "JavaScript": GenerateTestCasesPromptJavaScript,
        # "C++": GenerateTestCasesPromptCPP,
    }

    translator = MultiLLMTestTranslator("Java", "JavaScript", translation_llm_models, test_generation_llm_models, prompt_strategies, test_gen_prompts)
    translator.translate()


def main():
    print("Starting translation with dataset-provided tests...")
    run_dataset_translation()

    print("\nStarting translation with same LLM-generated tests...")
    run_llm_test_translation()

    print("\nStarting translation with different LLM-generated tests...")
    run_multi_llm_test_translation()


if __name__ == "__main__":
    main()