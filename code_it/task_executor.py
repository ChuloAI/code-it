"""This modules experiments building logic from scratch, without langchain."""
from dataclasses import dataclass
import logging
from code_it.code_editor.python_editor import PythonCodeEditor
from code_it.agents.planner import Planner
from code_it.agents.coder import Coder
from code_it.agents.refactor import Refactor
from code_it.agents.dependency_tracker import DependencyTracker
from code_it.models import HTTPBaseLLM
from typing import Callable

logger = logging.getLogger(__name__)

ANSWER_PATTERN = r"[a-zA-Z]+"
DEPENDENCY_BLACKLIST = set(["random", "json"])


def _trim_md(code_editor):
    if code_editor.source_code:
        code_editor.source_code[0] = code_editor.source_code[0].replace("```python", "")
        code_editor.source_code[-1] = code_editor.source_code[-1].replace("```", "")
        code_editor.overwrite_code(code_editor.display_code())


@dataclass
class TaskExecutionConfig:
    execute_code = True
    install_dependencies = True
    dependency_samples = 1
    max_refactor_attempts = 5
    dependency_install_attempts = 5
    planner_temperature = 0.2
    coder_temperature = 0.05
    refactor_temperature = 0.5
    dependency_tracker_temperature = 0.2


class TaskExecutor:
    def __init__(
        self,
        code_editor: PythonCodeEditor,
        refactored_code_editor: PythonCodeEditor,
        model_builder: Callable[[], HTTPBaseLLM],
        config: TaskExecutionConfig,
    ) -> None:
        self.code_editor = code_editor
        self.refactored_code_editor = refactored_code_editor
        self.config = config

        # Planner
        planner_llm = model_builder()
        planner_llm.set_parameter("temperature", config.planner_temperature)
        self.planner = Planner(planner_llm)

        # Coder
        coder_llm = model_builder()
        coder_llm.set_parameter("temperature", config.coder_temperature)
        self.coder = Coder(coder_llm)

        # Refactor
        refactoring_llm = model_builder()
        refactoring_llm.set_parameter("temperature", config.refactor_temperature)
        refactoring_llm.set_parameter("max_new_tokens", 1024)

        self.refactor = Refactor(refactoring_llm)

        # Dependency tracker
        dependency_tracker_llm = model_builder()
        dependency_tracker_llm.set_parameter(
            "temperature", config.dependency_tracker_temperature
        )
        self.dependency_tracker = DependencyTracker(dependency_tracker_llm)

    def execute(self, task: str):

        # Generating a coding plan
        plan = self.planner.execute_task(task=task)
        logger.info(type(plan))
        logger.info("Parsed plan: %s", plan)

        # Dependency installation
        installed_dependencies = False
        attempt = 0

        if self.config.execute_code and self.config.install_dependencies:
            while not installed_dependencies and attempt < self.config.dependency_install_attempts:
                dependencies = []
                for _ in range(self.config.dependency_samples):
                    dep = self.dependency_tracker.execute_task(plan="\n".join(plan))
                    for d in dep:
                        d = d.replace("-", "")
                        if d in DEPENDENCY_BLACKLIST:
                            continue
                        dependencies.append(d)

                dependencies = list(set(dependencies))
                logger.info("Dependencies: %s", dependencies)

                logger.info("Dependency lines: %s", dependencies)
                for dependency in dependencies:
                    self.refactored_code_editor.add_dependency(dependency)

                self.refactored_code_editor.create_env()
                process = self.refactored_code_editor.install_dependencies()
                if process.returncode != 0:
                    logger.error("Dependency install failed for: %s", "\n".join(dependencies))
                    attempt += 1

                else:
                    installed_dependencies = True

            if attempt >= self.config.dependency_install_attempts:
                raise ValueError("Failed to install dependencies")

            logger.info("Installed dependencies successfully!")

        # Coding
        for step in plan:
            logger.info("Coding step: %s", step)
            new_code = self.coder.execute_task(
                subtask=step, source_code=self.code_editor.display_code()
            )
            self.code_editor.add_code(new_code)
            logger.info("Trimming MD syntax")
            _trim_md(self.code_editor)

        logger.info("Finished generating code!")

        logger.info("Current code: %s", self.code_editor.display_code())


        # Refactoring
        for i in range(self.config.max_refactor_attempts):
            logger.info("After refactoring, attempt: %s", i)
            refactored = self.refactor.execute_task(
                source_code=self.code_editor.display_code(), objective=task, plan="\n".join(plan)
            )
            self.refactored_code_editor.overwrite_code(refactored)
            _trim_md(self.refactored_code_editor)

            logger.info(self.refactored_code_editor.display_code())

            if not self.config.execute_code:
                return self.refactored_code_editor.display_code()

            result = self.refactored_code_editor.run_code()

            if "Succeeded" in result:
                break

        if "Succeeded" in result:
            logger.info("Source code is functional!")
            return "Task Success: " + result
        else:
            logger.info("Failed to generate an executable source code.")
            return "Task Failed: " + result
