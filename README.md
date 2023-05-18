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


## Using it with Langchain


### The PipInstall action

### The ExecuteCodeTask action



## Modifying the behavior
When you're importing `code_it` package in your own code, you can change some settings on how it should behave. Specifically, these are the supported config options at the moment:
```python

```







