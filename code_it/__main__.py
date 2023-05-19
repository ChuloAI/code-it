import logging

from code_it.code_editor.python_editor import PythonCodeEditor
from code_it.models import build_text_generation_web_ui_client_llm, build_llama_base_llm
from code_it.task_executor import TaskExecutor, TaskExecutionConfig


import guidance
# set the default language model used to execute guidance programs
guidance.llm = guidance.llms.TextGenerationWebUI()
guidance.llm.caching = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

code_editor = PythonCodeEditor()

model_builder = build_text_generation_web_ui_client_llm

config = TaskExecutionConfig()

task_executor = TaskExecutor(code_editor, model_builder, config)

with open("task.txt", "r") as fp:
    task = fp.read()
    task_executor.execute(task)
