
class DependencyTracker:
    def __init__(self) -> None:
        self.stop_string = "end of planning flow"
        self.prompt_template = """
You're an AI master at planning and breaking down a coding task into smaller, tractable chunks.
You will be given a task, please helps us find the necessary python packages to install, thinking it through, step-by-step.

First, let's see an example of what we expect:

Task: Fetch the contents of the endpoint 'https://example.com/api' and write to a file
Requirements:
requests 

END OF PLANNING FLOW


Example 2:

Task: Connect to a Database
Requirements:
psycopg2

END OF PLANNING FLOW

Now let's begin with a real task. Remember you should break it down into tractable implementation chunks, step-by-step, like in the example.
If you plan to define functions, make sure to name them appropriately.
If you plan to use libraries, make sure to say which ones exactly.
Your output plan should NEVER modify an existing code, only add new code.
Keep it simple, stupid

Finally, remember to add 'End of planning flow' at the end of your planning.

Task: '{task}'.
Requirements:
"""
    
    def parse_output(self, output):
        output = output.lower()
        if self.stop_string in output:
            output = output.split(self.stop_string)[0]
        return [step for step in output.split("\n") if len(step) > 10]
