"""This agent does not work well, needs to be redone."""

from code_it.agents.base import BaseAgent


class Debugger(BaseAgent):
    def __init__(self, llm) -> None:
        super().__init__(llm)
        self.stop_string = "New Code:"
        self.prompt_template = """You're an expert python programmer AI Agent. You solve problems by using Python code,
and you're capable of providing code snippets, debugging and much more, whenever it's asked of you. You are usually given
an existing source code that has bugs. You should make it better by fixing the errors.

To fullfill your task, you'll receive the existing source code and the last result of attempting to execute it. 
There's usually a Traceback in the the error, mentioning the offending line and the raised exception.
You SHOULD USE this information to solve the error. Do this step-by-step.

Example:

Subtask: Write a code to print 'hello, world'
Source Code:
print('hello, world'
Error: 
Stderr:b'Traceback (most recent call last):\n  File "/home/paolo/code-it/persistent_source.py", line 1, in <module>\n    print('hello, world'\Syntax Error: unclosed )\n'
Thought: I should close the parenthesis on the line that prints hello world
New Code:
print('hello, world')
Subtask:

Notice that you once you finish the subtask, you should add the word 'Subtask:' in a new line,
like in the example above.

You should ALWAYS output the full code. 

Example 2:

Subtask: Write a code to sum x +y
Source Code:
x + y
Error: 
Stderr:b'Traceback (most recent call last):\n  File "/home/paolo/code-it/persistent_source.py", line 1, in <module>\n    x\nName Error: x is not defined\n'
Thought: I should close the parenthesis on the line that prints hello world
New Code:
x = 2
x + y
Subtask:


Now please help with the subtask below.

Subtask: {task}
Source Code: {source_code}
Error: {error}
Thought:
"""

    def parse_output(self, result):
        parsed = result
        if self.stop_string in result:
            parsed = parsed.split(self.stop_string)[1]
        if "```python" in result:
            parsed = parsed.split("```python")[1]
        if "```" in parsed:
            return parsed.split("```")[0]
        return parsed
