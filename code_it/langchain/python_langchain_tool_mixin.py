from code_it.langchain.base_langchain_tool_mixin import LangchainToolMixin
from code_it.code_editor.python_editor import PythonCodeEditor
from langchain.agents import Tool


class LangchainPythonToolMixin(LangchainToolMixin, PythonCodeEditor):
    def __init__(self, filename="persistent_source.py") -> None:
        super().__init__()
        self.filename = filename
        # Always create env
        self.create_env()

    def pip_install(self, dependency):
        """Promptly install dependencies."""
        # Trim pip install, we're already injecting it.
        dependency = dependency.replace("pip install", "").strip()
        self.add_dependency(dependency)
        completed_process = self.install_dependencies()
        succeeded = "Succeeded" if completed_process.returncode == 0 else "Failed"
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        return f"Program {succeeded}\nStdout:{stdout}\nStderr:{stderr}"

    def build_pip_install(self):
        return Tool(
            name="PipInstall",
            func=self.pip_install,
            description="""Use to install a new dependency. Example:
Action: PipInstall
Action Input:
requests

Observation: <result of installation>
""",
        )
