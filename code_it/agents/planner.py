from code_it.agents.base import BaseAgent
import guidance

class Planner(BaseAgent):
    def __init__(self, llm) -> None:
        super().__init__(llm)
        self.stop_string = "End of planning flow."
        self.guidance_output_variables = ["step"]
        self.prompt_template = guidance("""
You're an AI master at planning and breaking down a coding task into smaller, tractable chunks.
You will be given a task, please helps us thinking it through, step-by-step.

First, let's see an example of what we expect:

Task: Fetch the contents of the endpoint 'https://example.com/api' and write to a file
Steps:
1. I should import the requests library
2. I should use requests library to fetch the results from the endpoint 'https://example.com/api' and save to a variable called response
3. I should access the variable response and parse the contents by decoding the JSON contents
4. I should open a local file in write mode and use the json library to dump the results.

END OF PLANNING FLOW


Example 2:

Task: Write a random number to a file
Steps:
Step 1. I shold import the random library.
Step 2. I should define the output file name.
Step 3. I open a file and write the random number into it.

END OF PLANNING FLOW

Now let's begin with a real task. Remember you should break it down into tractable implementation chunks, step-by-step, like in the example.
If you plan to define functions, make sure to name them appropriately.
If you plan to use libraries, make sure to say which ones exactly. BE PRECISE.
Your output plan should NEVER modify an existing code, only add new code.
Keep it simple, stupid

Finally, remember to add 'End of planning flow' at the end of your planning.

Task: '{{task}}'.
Steps:
{{#geneach 'step' num_iterations=6}}
Step {{gen 'this' stop='\\n'}}
{{/geneach}}

""")
