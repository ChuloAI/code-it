import abc


class BaseAgent:
    def __init__(self, llm) -> None:
        self.llm = llm

    @abc.abstractmethod
    def parse_output(self, raw_result, parsed_output):
        raise NotImplementedError()

    def execute_task(self, **kwargs):
        prompt = self.prompt_template.format(**kwargs)
        raw_result = self.llm._call(prompt, stop=[self.stop_string])
        parsed_result = self.parse_output(raw_result)
        return parsed_result
