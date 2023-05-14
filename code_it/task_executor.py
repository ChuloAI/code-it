"""This modules experiments building logic from scratch, without langchain."""
from dataclasses import dataclass
import logging
from code_it.code_editor.python_editor import PythonCodeEditor
from code_it.agents.planner import Planner
from code_it.agents.coder import Coder
from code_it.agents.linter import Linter
from code_it.agents.dependency_tracker import DependencyTracker
from code_it.models import HTTPBaseLLM
from typing import Callable
from pylint import epylint as lint


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
    apply_linter = True
    dependency_samples = 3
    max_refactor_attempts = 5
    dependency_install_attempts = 5
    planner_temperature = 0
    coder_temperature = 0
    refactor_temperature = 0.3
    dependency_tracker_temperature = 0.2


class TaskExecutor:
    def __init__(
        self,
        code_editor: PythonCodeEditor,
        model_builder: Callable[[], HTTPBaseLLM],
        config: TaskExecutionConfig,
    ) -> None:
        self.code_editor = code_editor
        self.config = config

        # Planner
        planner_llm = model_builder()
        planner_llm.set_parameter("temperature", config.planner_temperature)
        self.planner = Planner(planner_llm)

        # Coder
        coder_llm = model_builder()
        coder_llm.set_parameter("temperature", config.coder_temperature)
        coder_llm.set_parameter("max_new_tokens", 1024)

        self.coder = Coder(coder_llm)

        # Linter
        linter_llm = model_builder()
        linter_llm.set_parameter("temperature", config.refactor_temperature)
        linter_llm.set_parameter("max_new_tokens", 1024)
        self.linter = Linter(linter_llm)

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
                        d = d.replace("-", "").strip()
                        if " " in d:
                            d = d.split(" ")[0]

                        if len(d) < 2 or d in DEPENDENCY_BLACKLIST:
                            continue
                        dependencies.append(d)

                if not dependencies:
                    break

                dependencies = list(set(dependencies))
                logger.info("Dependencies: %s", dependencies)

                logger.info("Dependency lines: %s", dependencies)
                for dependency in dependencies:
                    self.code_editor.add_dependency(dependency)

                self.code_editor.create_env()
                process = self.code_editor.install_dependencies()
                if process.returncode != 0:
                    logger.error("Dependency install failed for: %s", "\n".join(dependencies))
                    attempt += 1

                else:
                    installed_dependencies = True

            if attempt >= self.config.dependency_install_attempts:
                raise ValueError("Failed to install dependencies")

            logger.info("Installed dependencies successfully!")

        # Coding
        for i in range(self.config.max_refactor_attempts):
            logger.info("Coding, attempt: %s", i)
            refactored = self.coder.execute_task(
                source_code=self.code_editor.display_code(), objective=task, plan="\n".join(plan)
            )
            self.code_editor.overwrite_code(refactored)
            _trim_md(self.code_editor)

            logger.info(self.code_editor.display_code())

            if self.config.apply_linter:
                logger.info("Applying linter...")
                (pylint_stdout, _) = lint.py_run(self.code_editor.filename, return_std=True)
                pylint_stdout = pylint_stdout.getvalue()
                logger.info(pylint_stdout)

                new_code = self.linter.execute_task(
                    source_code=self.code_editor.display_code(),
                    stdout=pylint_stdout,
                )
                logger.warn("Linted code: %s", new_code)
                if new_code:
                    self.code_editor.overwrite_code(new_code)

            if not self.config.execute_code:
                return self.code_editor.display_code()

            result = self.code_editor.run_code()

            if "Succeeded" in result:
                break

        logger.info("Finished generating code!")

        if "Succeeded" in result:
            logger.info("Source code is functional!")
            return "Task Success: " + result
        else:
            logger.info("Failed to generate an executable source code.")
            return "Task Failed: " + result
