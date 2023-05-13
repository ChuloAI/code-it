"""This modules experiments building logic from scratch, without langchain."""
import logging
from code_it.code_editor.python_editor import PythonCodeEditor
from code_it.planner import Planner
from code_it.coder import Coder
from code_it.refactor import Refactor
from code_it.debugger import Debugger
from code_it.dependency_tracker import DependencyTracker

logger = logging.getLogger(__name__)

ANSWER_PATTERN = r"[a-zA-Z]+"


class TaskExecutor:
    def __init__(self, code_editor: PythonCodeEditor, model_builder) -> None:
        self.code_editor = code_editor
        self.planner_llm = model_builder()
        self.coder_llm = model_builder()
        self.refactoring_llm = model_builder()
        self.debugger_llm = model_builder()
        self.dependency_tracker_llm = model_builder()

        self.planner = Planner()
        self.coder = Coder()
        self.refactor = Refactor()
        self.debugger = Debugger()
        self.dependency_tracker = DependencyTracker()

    def execute(self, task: str):
        dependency_prompt = self.dependency_tracker.prompt_template.format(task=task)
        dependencies = self.dependency_tracker_llm._call(dependency_prompt, stop=[self.dependency_tracker.stop_string])
        dependencies = self.dependency_tracker.parse_output(dependencies)
        logger.info("Dependencies: %s", dependencies)

        logger.info("Dependency lines: %s", dependencies)
        for dependency in dependencies:
            self.code_editor.add_dependency(dependency)

        self.code_editor.create_env()
        self.code_editor.install_dependencies()

        planner_prompt = self.planner.prompt_template.format(task=task)
        plan = self.planner_llm._call(planner_prompt, stop=[self.planner.stop_string])
        plan = self.planner.parse_output(plan)
        logger.info(type(plan))
        logger.info("Parsed plan: %s", plan)

        for step in plan:
            logger.info("Coding step: %s", step)
            coder_prompt = self.coder.prompt_template.format(subtask=step, source_code=self.code_editor.display_code())
            debugging_result = self.coder_llm._call(coder_prompt, stop=[self.coder.stop_string])
            new_code = self.coder.parse_output(debugging_result)
            self.code_editor.add_code(new_code)
        logger.info("Finished generating code!")


        logger.info("Current code: %s", self.code_editor.display_code())
        refactored = self.refactoring_llm._call(self.refactor.prompt_template.format(source_code=self.code_editor.display_code(), task=task), stop=[self.coder.stop_string])
        logger.info("After refactoring")
        self.code_editor.overwrite_code(refactored)
        logger.info(self.code_editor.display_code())


        logger.info("Trimming MD syntax")
        def trim_md(code_editor):
            code_editor.source_code[0] = code_editor.source_code[0].replace("```python", "")
            code_editor.source_code[-1] = code_editor.source_code[-1].replace("```", "")
            code_editor.overwrite_code(code_editor.display_code())

        trim_md(self.code_editor)
        result = self.code_editor.run_code()
        logger.info("Result", result)
        if "Succeeded" in result:
            logger.info("Source code is functional!")
        if "Failed" in result:
            logger.info("Failed to generate a working source code, let's debug it.")
            for i in range(5):
                debugger_prompt = self.debugger.prompt_template.format(source_code=self.code_editor.display_code(), task=task, error=result.split("Stderr")[1])
                debugging_result = self.debugger_llm._call(debugger_prompt, stop=[self.coder.stop_string])
                new_code = self.debugger.parse_output(debugging_result)
                self.code_editor.overwrite_code(new_code)
                result = self.code_editor.run_code()
                if "Failed" not in result:
                    break
                logger.info("Still broken, let's try again...")


        if "Succeeded" in result:
            logger.info("Source code is functional!")
            return "Task Success: " + result
        else:
            logger.info("Failed to generate an executable source code.")
            return "Task Failed: " + result