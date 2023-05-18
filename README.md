# code-it

Code-it is simultaneously:

1. A standalone package to generate code and execute with LLMs
2. An importable tool into langchain


This is a highly experimental project, the quality of the generations may not be high enough for production usage.

Code-it leverages LLMs to generate code - unlike other solutions, it doesn't try to rely on the smartness of LLMs, but rather assume they are rather dumb and perform several mistakes along the way. It applies a simple algorithm to iteratively code towards it's task objective, in a similar way a programmer might do. This algorithm is implemented with control statements and different prompts to steer the LLM at performing the correct action.

It is **not** an autonomous agent - at most, we could call it semi-autonomous.


## Overview Idea
![Overview Diagram](/overview_diagram.jpg?raw=true "Optional Title")


## Installation

1. Setup https://github.com/oobabooga/text-generation-webui with API enabled
2. Install it through pip / git on your project. For, you can define this line in your project requirements.txt:
```text
code_it @ git+https://github.com/paolorechia/code-it
```
Note that I did not yet have tags or a PyPi package, as I'm not sure how useful this package will be in the future. 

3. Locally as a standalone program with your current Python shell / virtualenv:

```bash
git clone https://github.com/paolorechia/code-it
cd code-it
pip install -r requirements.txt
```

## Running it as a standalone program (using the package `__main__.py`)
WARNING: the LLM will run arbitrary code, use it at your own risk.
Execute the main:
`python3 -m code_it`

This will save the code in `persistent_source.py`

Change the task in the `task.txt` file to perform another task.

## Using it as a standalone package in your program
You can reuse the code from https://github.com/paolorechia/code-it/blob/main/code_it/__main__.py

Here's the base minimum code to use this library: 
```python
from code_it.code_editor.python_editor import PythonCodeEditor
from code_it.models import build_text_generation_web_ui_client_llm, build_llama_base_llm
from code_it.task_executor import TaskExecutor, TaskExecutionConfig


code_editor = PythonCodeEditor()
model_builder = build_llama_base_llm
config = TaskExecutionConfig()

task_executor = TaskExecutor(code_editor, model_builder, config)

with open("task.txt", "r") as fp:
    task = fp.read()
    task_executor.execute(task)
```

Here we import the `PythonCodeEditor`, currently the only supported editor, along with a llama LLM. Notice that this assumes a server running on 0.0.0.0:8000, which comes from my other repo: https://github.com/paolorechia/learn-langchain/blob/main/servers/vicuna_server.py

You can easily change this to instead use the text-generation-web-ui tool from oobagooba, by importing the builder: `build_text_generation_web_ui_client_llm`. Implementing your own model client should also be straightforward. Look at the source code in: https://github.com/paolorechia/code-it/blob/main/code_it/models.py

### Modifying the behavior
Notice that in the example above we imported the `TaskExecutionConfig`, let's look at this class:

```python
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
    dependency_install_attempts = 5
    planner_temperature = 0
    coder_temperature = 0
    linter_temperature = 0.3
    dependency_tracker_temperature = 0.2
```

You can change these parameters to change how the program behaves. Not all settings are always applied at the same time, for instance, if you change the `code_sampling_strategy` to `NO_SAMPLING`, then of course the config parameter `sampling_temperature_multiplier` is not used.

To understand these settings better, you should read the task execution code directly, as there is no detailed documentation for this yet: https://github.com/paolorechia/code-it/blob/main/code_it/task_executor.py


## Using it with Langchain

### Task Execution Tool
Here's an example using my other repo: https://github.com/paolorechia/learn-langchain/blob/main/langchain_app/executor_tests/chuck_norris_joke.py


```python
from langchain.agents import initialize_agent, AgentType
from langchain_app.models.vicuna_request_llm import VicunaLLM

from code_it.models import build_llama_base_llm
from code_it.langchain.code_it_tool import CodeItTool
from code_it.task_executor import TaskExecutionConfig

llm = VicunaLLM()
config = TaskExecutionConfig()
print(config)
config.install_dependencies = False
config.execute_code = True
code_editor = CodeItTool(build_llama_base_llm, config)

tools = [
    code_editor.build_execute_task(),
]

agent = initialize_agent(
    tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

agent.run(
    """

Remember to use the following format:
Action: <>
Action Input:
<>

Question: The endpoint https://api.chucknorris.io/jokes/random returns a joke about Chuck Norries

1. Write a python Program that fetches a joke from this endpoint.
2. Extract the joke from the response. Access the 'value' in the JSON to extract it.
3. Prints the joke to the screen.
"""
)
```


### The PipInstall action










