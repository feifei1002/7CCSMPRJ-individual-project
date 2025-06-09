import subprocess
import os
from config import EXECUTION_COMMANDS


class CodeRunner:
    @staticmethod
    def run_python(file_path):
        return subprocess.run(["python", file_path], capture_output=True, text=True)

    @staticmethod
    def run_javascript(file_path):
        return subprocess.run(["node", file_path], capture_output=True, text=True)

    @staticmethod
    def run_java(file_path):
        dir_path = os.path.dirname(file_path)
        subprocess.run(["javac", file_path], cwd=dir_path)
        class_file = file_path.replace(".java", "")
        return subprocess.run(["java", "Main"], cwd=dir_path, capture_output=True, text=True)

    @staticmethod
    def run_cpp(file_path):
        dir_path = os.path.dirname(file_path)
        output_file = os.path.join(dir_path, "a.out")
        subprocess.run(["g++", file_path, "-o", output_file])
        return subprocess.run([output_file], capture_output=True, text=True)

    @staticmethod
    def run_go(file_path):
        return subprocess.run(["go", "run", file_path], capture_output=True, text=True)

    @classmethod
    def execute(cls, language, file_path):
        runners = {
            "Python": cls.run_python,
            "JavaScript": cls.run_javascript,
            "Java": cls.run_java,
            "C++": cls.run_cpp,
            "Go": cls.run_go
        }

        runner = runners.get(language)
        if not runner:
            raise ValueError(f"Unsupported language: {language}")

        try:
            result = runner(file_path)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)