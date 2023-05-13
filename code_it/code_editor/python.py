from code_editor.base import CodeEditorTooling
from code_editor.virtualenv_manager import VirtualenvManager

class PythonCodeEditor(CodeEditorTooling):
    def __init__(self, filename="persistent_source.py") -> None:
        super().__init__(filename, interpreter="python3")
        self.venv = VirtualenvManager()
    
    def add_dependency(self, dependency):
        self.venv.dependencies.append(dependency)

    def create_env(self):
        self.venv.create_env()

    def activate_env(self):
        self.venv.activate_env()

    def install_dependencies(self):
        self.venv.install_dependencies()
