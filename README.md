# code-it

This is a highly experimental project. Code-it leverages LLMs to generate code - unlike other solutions, it doesn't try to rely on the smartness of LLMs, but rather assume they are rather dumb and perform several mistakes along the way. It applies a simple algorithm to iteratively code towards it's task objective, in a similar way a programmer might do. This algorithm is implemented with control statements and different prompts to steer the LLM at performing the correct action.

It is **not** an autonomous agent - at most, we could call it semi-autonomous.


## Installation

1. Setup https://github.com/oobabooga/text-generation-webui with API enabled
2. `pip install -r requirements.txt`

## Running it

WARNING: the LLM will run arbitrary code, use it at your own risk.
Execute the main:
`python3 -m code_it`

This will start an infinite loop you can use to test executing tasks.
The execution of the task updates the code in a local file called `persistent_source.py`
