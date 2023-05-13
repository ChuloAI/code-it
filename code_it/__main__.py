"""This modules experiments building logic from scratch, without langchain."""
import logging
import sys
from code_it.models import build_text_generation_web_ui_client_llm, build_llama_base_llm
from code_it.code_editor.python_editor import PythonCodeEditor
from code_it.planner import Planner
from code_it.coder import Coder
from code_it.refactor import Refactor
from code_it.debugger import Debugger
from code_it.dependency_tracker import DependencyTracker


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

ANSWER_PATTERN = r"[a-zA-Z]+"

code_editor = PythonCodeEditor()
model_builder = build_llama_base_llm
# model_builder = build_text_generation_web_ui_client_llm

planner_llm = model_builder()
coder_llm = model_builder()
refactoring_llm = model_builder()
debugger_llm = model_builder()
dependency_tracker_llm = model_builder()

planner = Planner()
coder = Coder()
refactor = Refactor()
debugger = Debugger()
dependency_tracker = DependencyTracker()

with open("task.txt") as fp:
    task = fp.read()

dependency_prompt = dependency_tracker.prompt_template.format(task=task)
dependencies = dependency_tracker_llm._call(dependency_prompt, stop=[dependency_tracker.stop_string])
dependencies = dependency_tracker.parse_output(dependencies)
logger.info("Dependencies: %s", dependencies)

logger.info("Dependency lines: %s", dependencies)
for dependency in dependencies:
    code_editor.add_dependency(dependency)

code_editor.create_env()
code_editor.install_dependencies()

planner_prompt = planner.prompt_template.format(task=task)
plan = planner_llm._call(planner_prompt, stop=[planner.stop_string])
plan = planner.parse_output(plan)
logger.info(type(plan))
logger.info("Parsed plan: %s", plan)

for step in plan:
    logger.info("Coding step: %s", step)
    coder_prompt = coder.prompt_template.format(subtask=step, source_code=code_editor.display_code())
    debugging_result = coder_llm._call(coder_prompt, stop=[coder.stop_string])
    new_code = coder.parse_output(debugging_result)
    code_editor.add_code(new_code)
logger.info("Finished generating code!")


logger.info("Current code: %s", code_editor.display_code())
refactored = refactoring_llm._call(refactor.prompt_template.format(source_code=code_editor.display_code(), task=task), stop=[coder.stop_string])
logger.info("After refactoring")
code_editor.overwrite_code(refactored)
logger.info(code_editor.display_code())


logger.info("Trimming MD syntax")
def trim_md(code_editor):
    code_editor.source_code[0] = code_editor.source_code[0].replace("```python", "")
    code_editor.source_code[-1] = code_editor.source_code[-1].replace("```", "")
    code_editor.overwrite_code(code_editor.display_code())

trim_md(code_editor)
result = code_editor.run_code()
logger.info("Result", result)
if "Succeeded" in result:
    logger.info("Source code is functional!")
if "Failed" in result:
    logger.info("Failed to generate a working source code, let's debug it.")
    for i in range(5):
        debugger_prompt = debugger.prompt_template.format(source_code=code_editor.display_code(), task=task, error=result.split("Stderr")[1])
        debugging_result = debugger_llm._call(debugger_prompt, stop=[coder.stop_string])
        new_code = debugger.parse_output(debugging_result)
        code_editor.overwrite_code(new_code)
        result = code_editor.run_code()
        if "Failed" not in result:
            break
        logger.info("Still broken, let's try again...")


if "Succeeded" in result:
    logger.info("Source code is functional!")
else:
    logger.info("Failed to generate an executable source code.")
