"""This modules experiments building logic from scratch, without langchain.

It needs some refactoring :)
"""
from dataclasses import dataclass
import logging
from code_it.code_editor.python_editor import PythonCodeEditor
from code_it.agents.complexity_analyser import ComplexityAnalyser
from code_it.agents.planner import Planner
from code_it.agents.coder import Coder
from code_it.agents.dependency_tracker import DependencyTracker
from code_it.models import HTTPBaseLLM
from typing import Callable
from pylint import epylint as lint
import requests
from typing import List

logger = logging.getLogger(__name__)

ANSWER_PATTERN = r"[a-zA-Z]+"

PYLINT_SCORE_SUBSTRING = "Your code has been rated at "
NO_SAMPLING = "NO_SAMPLING"
PYLINT = "PYLINT"

DEPENDENCY_BLACKLIST = set(["random", "json"])
SUPPORTED_SAMPLING_STRATEGIES = set([PYLINT])

def _trim_md(code_editor):
    if code_editor.source_code:
        code_editor.source_code[0] = code_editor.source_code[0].replace("```python", "")
        code_editor.source_code[-1] = code_editor.source_code[-1].replace("```", "")
        code_editor.overwrite_code(code_editor.display_code())

# TODO: add validation to the config

@dataclass
class TaskExecutionConfig:
    execute_code = True
    install_dependencies = True
    apply_linter = True
    check_package_is_in_pypi = True
    log_to_stdout = True
    coding_samples = 3
    code_sampling_strategy = "PYLINT"
    sampling_temperature_multipler = 0.1
    dependency_samples = 3
    max_coding_attempts = 5
    planner_temperature = 0
    coder_temperature = 0
    linter_temperature = 0.3
    dependency_tracker_temperature = 0.2
    complexity_analyser_temperature = 0.1

class TaskExecutor:
    def __init__(
        self,
        code_editor: PythonCodeEditor,
        model_builder: Callable[[], HTTPBaseLLM],
        config: TaskExecutionConfig,
    ) -> None:
        self.code_editor = code_editor
        self.config = config
        # ComplexityAnalyser
        self.complexity_analyser = ComplexityAnalyser(
            model_builder()
        )
        self.planner = Planner(model_builder())
        self.coder = Coder(model_builder())
        self.dependency_tracker = DependencyTracker(model_builder())


    def install_dependencies(self, plan: List[str]) -> List[str]:
        dependencies = []
        for _ in range(self.config.dependency_samples):
            dependency_output = self.dependency_tracker.execute_task(plan="\n".join(plan))
            logger.info("Dependency task output: %s", dependency_output)
            deps = dependency_output["requirements"].split("\n")
            for d in deps:
                d = d.replace("-", "").strip()
                if " " in d:
                    d = d.split(" ")[0]
                logger.info("%s", d)

                if self.config.check_package_is_in_pypi:
                    url = f'https://pypi.org/project/{d}'
                    res = requests.get(url)
                    if res.status_code != 200:
                        pass

                if len(d) < 2 or d in DEPENDENCY_BLACKLIST:
                    continue

                dependencies.append(d)

        if not dependencies:
            logger.info("No dependencies found!")
            return []

        dependencies = list(set(dependencies))
        logger.info("Dependencies: %s", dependencies)

        logger.info("Dependency lines: %s", dependencies)
        for dependency in dependencies:
            self.code_editor.add_dependency(dependency)

        self.code_editor.create_env()
        process = self.code_editor.install_dependencies()
        if process.returncode != 0:
            raise ValueError("Failed to install dependencies")

        logger.info("Installed dependencies successfully!")
        return dependencies


    def execute(self, task: str):
        # Generating a coding plan

        complexity_output = self.complexity_analyser.execute_task(task=task)
        print("Complexity output:", complexity_output)

        planner_output = self.planner.execute_task(task=task, steps=complexity_output["required_steps"], **complexity_output)
        plan = planner_output["steps"]
        logger.info(type(plan))
        logger.info("Parsed plan: %s", plan)


        if self.config.execute_code and self.config.install_dependencies:
            self.install_dependencies(plan)

        for step in plan:
            coder_output = self.coder.execute_task(objective=task, plan="\n".join(plan), current_step=step, source_code=self.code_editor.display_code())
            self.code_editor.add_code(coder_output["new_code"])

        logger.info("Finished generating code!")
        print(self.code_editor.display_code())

        result = self.code_editor.run_code()
        if "Succeeded" in result:
            logger.info("Source code is functional!")
            return "Task Success: " + result
        else:
            logger.info("Failed to generate an executable source code.")
            return "Task Failed: " + result
