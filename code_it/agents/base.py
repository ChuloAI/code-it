import abc
from guidance import Program

class BaseAgent:
    def __init__(self, llm) -> None:
        self.llm = llm

    @abc.abstractmethod
    def parse_output(self, raw_result, parsed_output):
        raise NotImplementedError()

    def execute_task(self, **kwargs):
        guidance_program: Program = self.prompt_template
        program_result = guidance_program(**kwargs, stream=False, async_mode=False, caching=False)
        output = {}
        for output_var in self.guidance_output_variables:
            output[output_var] = program_result[output_var]
        return output