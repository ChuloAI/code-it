from code_it.code_editor.base_langchain_tool_mixin import LangchainToolMixin
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


    def run_code_simplified(self, input_code):
        self.overwrite_code(input_code)
        return self.run_code()

    def build_run_code(self, input_code):
        return Tool(
            name="RunCode",
            func=self.run_code_simplified,
            description="""Use to execute the script. Should always be called like this:

Action: RunCode
Action Input:
print("hello, world")

Observation:Program Succeeded
Stdout:b'Hello, world!'
Stderr:b''

Thought: In this example, the output of the program was b'Hello, world!'
Task Completed: the task was successfully completed

Example 2 (failure example):
Action: RunCode
Action Input:
print("hello, world)
Observation:Program Failed
Stdout:b''
Stderr:b''^^^^^\nSyntaxError: invalid syntax\n'

Thought: In this example, the program failed due to SyntaxError
"""
)

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

