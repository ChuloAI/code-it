from code_it.code_editor.base import CodeEditorTooling
from langchain.agents import Tool

class LangchainToolMixin(CodeEditorTooling):
    def __init__(self) -> None:
        super().__init__()

    def build_add_code_tool(self):
        return Tool(
            name="CodeEditorAddCode",
            func=self.add_code,
            description="""Use to add new lines of code. Example:
Action: CodeEditorAddCode
Action Input:
print("foo bar")

Observation: print("foo bar")

    Example 2. One can also use it to add several lines of code simultaneously:

Action: CodeEditorAddCode
Action Input: 
x = 2 + 3

Observation: x = 2 + 3

""",
        )

    def build_change_code_line_tool(self):
        return Tool(
            name="CodeEditorChangeCodeLine",
            func=self.change_code_line,
            description="""Use to modify an existing line of code. First line of input is line number and second line is new line of code to insert.

            Example that modifies line 3:

Source Code:
def my_func(x, y):
    return x * y
my_func(2, 3)

Action: CodeEditorChangeCodeLine
Action Input:
3
print("Line 3 now prints this")

Observation:
my_func(x, y):
    return x * y
print("Line 3 now prints this")

""",
        )
    
    def build_delete_code_lines_tool(self):
        return Tool(
            name="CodeEditorDeleteLine",
            func=self.delete_code_lines,
            description="""Use to delete lines of code.
            
            Example, to delete lines 1 and 3 of the source code.

Source Code:
def my_func(x, y):
    return x * y
my_func(2, 3)

Action: CodeEditorDeleteLine
Action Input:
1, 3
Observation: 
return x * y

""",
        )

    def build_run_tool(self):
        return Tool(
            name="CodeEditorRunCode",
            func=self.run_code,
            description="""Use to execute the script. Should always be called like this:

Action: CodeEditorRunCode
Action Input:
Observation: 
Observation:Program Succeeded
Stdout:b'Hello, world!'
Stderr:b''

Thought: In this example, the output of the program was b'Hello, world!'
Task Completed: the task was successfully completed

Example 2 (failure example):
Action: CodeEditorRunCode
Action Input:
Observation: 
Observation:Program Failed
Stdout:b''
Stderr:b''^^^^^\nSyntaxError: invalid syntax\n'

Thought: In this example, the program failed due to SyntaxError




""",
        )

    def build_display_code_tool(self):
        return Tool(
            name="CodeEditorDisplayCode",
            func=self.display_code,
            description="""Use to display current source code. Example:
Action: CodeEditorDisplayCode
Action Input:

Observation:
print("foo bar")
""",
        )