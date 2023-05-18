# code-it

Code-it is simultaneously:

1. A standalone package to generate code and execute with **local** LLMs.
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
config.install_dependencies = True
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

Question: Extract a joke from https://api.chucknorris.io/jokes/random - access the key 'value' from the returned JSON.
"""
)
```


### Using the Mixin class
The Mixin gives the option to use the pip install command from the `code_it` virtualenv manager, effectively adding package installation powers to your LLM inside langchain.

**Note that the Mixin does not work as well as the task execution tool.**

The model quite often fails to use the new actions appropriately.

Code from: https://github.com/paolorechia/learn-langchain/blob/main/langchain_app/agents/coder_plot_chart_mixin_test.py

```python
rom langchain.agents import (
    AgentExecutor,
    LLMSingleActionAgent,
    Tool,
    AgentOutputParser,
)
from langchain.prompts import StringPromptTemplate
from langchain import LLMChain
from langchain_app.models.vicuna_request_llm import VicunaLLM
from langchain.schema import AgentAction, AgentFinish

from code_it.langchain.python_langchain_tool_mixin import LangchainPythonToolMixin

import re
from typing import List, Union


llm = VicunaLLM()

code_editor = LangchainPythonToolMixin()

tools = [
    code_editor.build_add_code_tool(),
    code_editor.build_run_tool(),
    code_editor.build_pip_install()
]

template = """You're a programmer AI.

You are asked to code a certain task.
You have access to a Code Editor, that can be used through the following tools:

{tools}


You should ALWAYS think what to do next.

Use the following format:

Task: the input task you must implement
Current Source Code: Your current code state that you are editing
Thought: you should always think about what to code next
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: The result of your last action
... (this Thought/Action/Action Input/Source Code/Code Result can repeat N times)

Thought: I have finished the task
Task Completed: the task has been implemented

Example task:
Task: the input task you must implement

Thought: To start, we need to add the line of code to print 'hello world'
Action: CodeEditorAddCode
Action Input: 
print("hello world") end of llm ouput
Observation:None

Thought: I have added the line of code to print 'hello world'. I should execute the code to test the output
Action: CodeEditorRunCode
Action Input: 

Observation:Program Succeeded
Stdout:b'hello world\n'
Stderr:b''

Thought: The output is correct, it should be 'hello world'
Action: None
Action Input:
Output is correct

Observation:None is not a valid tool, try another one.

Thought: I have concluded that the output is correct
Task Completed: the task is completed.


REMEMBER: don't install the same package more than once

Now we begin with a real task!

Task: {input}
Source Code: {source_code}

{agent_scratchpad}

Thought:"""


# Set up a prompt template
class CodeEditorPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    code_editor: LangchainPythonToolMixin
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        kwargs["source_code"] = code_editor.display_code()
        kwargs["tools"] = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in self.tools]
        )
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)


prompt = CodeEditorPromptTemplate(
    template=template,
    code_editor=code_editor,
    tools=tools,
    input_variables=["input", "intermediate_steps"],
)


class CodeEditorOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        print("llm output: ", llm_output, "end of llm ouput")
        # Check if agent should finish
        if "Task Completed:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(
            tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output
        )


output_parser = CodeEditorOutputParser()

llm_chain = LLMChain(llm=llm, prompt=prompt)
llm = VicunaLLM()

tool_names = [tool.name for tool in tools]
agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:"],
    allowed_tools=tool_names,
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True
)

agent_executor.run(
    """
Your job is to plot an example chart using matplotlib. Create your own random data.
Run this code only when you're finished.
DO NOT add code and run into a single step.
"""
)
```









