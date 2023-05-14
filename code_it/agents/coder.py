from code_it.agents.base import BaseAgent


class Coder(BaseAgent):
    def __init__(self, llm) -> None:
        super().__init__(llm)
        self.stop_string = "Objective:"
        self.prompt_template = """"You're an expert python programmer AI Agent. You solve problems by using Python code,
and you're capable of providing code snippets, debugging and much more, whenever it's asked of you. You are usually given
an existing source code that's poorly written and contains many duplications. You should make it better by refactoring and removing errors.

You should fulfill your role in the example below:

Objective: Write a code to print 'hello, world'
Plan: 1. Call print function with the parameter 'hello, world' 
Source Code:
import os
import os
import os
print('hello, world')
Thought: The code contains duplication and an unused import. Here's an improved version.
New Code:
print('hello, world')
Objective:

Notice that you once you finish the subtask, you should add the word 'Objective:' in a new line,
like in the example above.

You should ALWAYS output the full code. 

Now please help with the subtask below.

Objective: {objective}
Plan: {plan}
Source Code: {source_code}
New Code:
"""

    def parse_output(self, result):
        if self.stop_string in result:
            result = result.split(self.stop_string)[1]
        return result
