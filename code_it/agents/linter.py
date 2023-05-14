from code_it.agents.base import BaseAgent


class Linter(BaseAgent):
    def __init__(self, llm) -> None:
        super().__init__(llm)
        self.start_string = "NewCode:"
        self.stop_string = "ExistingSourceCode:"
        self.prompt_template = """"You're AI tool that applies a linter to a Python Code and fixes the issues found. Think step-by-step.
You should fulfill your role like in the example below:

ExistingSourceCode:
import os
import os
files = os.listdir()
************* Module persistent_source
persistent_source.py:3:0: C0304: Final newline missing (missing-final-newline)
persistent_source.py:1:0: C0114: Missing module docstring (missing-module-docstring)
persistent_source.py:2:0: W0404: Reimport 'os' (imported line 1) (reimported)

------------------------------------------------------------------
Your code has been rated at 0.00/10 (previous run: 0.00/10, +0.00)


Programmer AI: I need to perform some modifications on the source code
1. There is a misssing newline.
2. Missing module docstring, I should add one
3. There are duplicated imports, I should remove one
NewCode:
\"\"\"Module to list files in current directory \"\"\"
import os
files = os.listdir()

ExistingSourceCode:

Notice that you once you finish the subtask, you should add the word 'ExistingSourceCode:' in a new line,
like in the example above.

Now please help with the subtask below.

ExistingSourceCode: {source_code}
Lint Stdout: {stdout}
Programmer AI:
"""

    def parse_output(self, result):
        print("Linter result", result)
        if self.stop_string not in result:
            result = result.split(self.stop_string)[0]

        if self.start_string not in result:
            return None

        result = result.split(self.start_string)[1]
        print("Parsed linter", result)
        return result
