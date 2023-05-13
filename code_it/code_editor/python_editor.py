import logging
from code_it.code_editor.base import CodeEditorTooling
from code_it.code_editor.virtualenv_manager import VirtualenvManager

logger = logging.getLogger(__name__)

class PythonCodeEditor(CodeEditorTooling):
    def __init__(self, filename="persistent_source.py") -> None:
        super().__init__(filename, interpreter="python3")
        self.venv = VirtualenvManager()
    
    def add_dependency(self, dependency):
        self.venv.add_dependency(dependency)

    def create_env(self):
        self.venv.create_env()
        self.interpreter = self.venv.python_interpreter
        logger.info("Python interpreter set to %s", self.interpreter)

    def install_dependencies(self):
        self.venv.install_dependencies()
