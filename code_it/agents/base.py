import abc
from guidance import Program
import guidance
from copy import deepcopy
import logging

MACRO_PREFIX="#####"
logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, llm) -> None:
        self.llm = llm

    @abc.abstractmethod
    def parse_output(self, raw_result, parsed_output):
        raise NotImplementedError()

    def execute_task(self, **kwargs):
        template = deepcopy(self.prompt_template)

        # Expand macro variables
        for macro_variable in self.macro_variables:
            logger.info("Expanding macro: %s", macro_variable)
            var_value = kwargs.pop(macro_variable)
            macro_key = f"{MACRO_PREFIX}{macro_variable}"
            logger.info("Should expand key '%s' into value '%s'", macro_key, var_value)
            template = template.replace(macro_key, var_value)

        logger.debug("Template: %s", template)

        logger.info("Reading input variables: %s", self.guidance_input_variables)
        input_vars = {}
        for input_var in self.guidance_input_variables:
            input_vars[input_var] = kwargs.pop(input_var)
        logger.info("Resolved guidance input variables: %s", input_vars)

        guidance_program: Program = guidance(template)
        program_result = guidance_program(**kwargs, stream=False, async_mode=False, caching=False, **input_vars)
        
        output = {}
        for output_var in self.guidance_output_variables:
            output[output_var] = program_result[output_var]
        return output