import logging

from code_it.code_editor.python_editor import PythonCodeEditor
from code_it.models import build_text_generation_web_ui_client_llm, build_llama_base_llm
from code_it.task_executor import TaskExecutor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

code_editor = PythonCodeEditor()

# model_builder = build_text_generation_web_ui_client_llm
model_builder = build_llama_base_llm

task_executor  = TaskExecutor(code_editor, model_builder)

with open("task.txt") as fp:
    task = fp.read()

task_executor.execute(task)