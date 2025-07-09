from datasets import load_dataset
from config import LANGUAGE_MAP
from src.config import FILE_EXTENSION


def get_dataset_name(language):
    return LANGUAGE_MAP.get(language, language)

def get_file_extension(language):
    return FILE_EXTENSION.get(language, language)

def load_test_dataset(target_language, split="test[:3]"):
    return load_dataset("THUDM/humaneval-x", get_dataset_name(target_language), split=split)

def load_code_dataset(source_language, split="test[:3]"):
    return load_dataset("THUDM/humaneval-x", get_dataset_name(source_language), split=split)