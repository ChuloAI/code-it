import logging

from code_it.code_editor.python_editor import PythonCodeEditor
from code_it.models import HTTPBaseLLM
from code_it.task_executor import TaskExecutor, TaskExecutionConfig
from langchain.agents import Tool


class CodeItTool:
    def __init__(self, model_builder: HTTPBaseLLM, config: TaskExecutionConfig) -> None:
        self.model_builder = model_builder

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )

    def execute_task(self, task):
        code_editor = PythonCodeEditor()
        task_executor = TaskExecutor(code_editor, self.model_builder)
        return task_executor.execute(task)

    def build_execute_task(self):
        return Tool(
            name="ExecuteCodingTask",
            func=self.execute_task,
            description="""Use it to execute a coding task. Example:
Action: ExecuteCodingTask
Action Input:
Print hello world to the terminal


Observation: <code execution logs>
""",
        )
