import logging

import openai
import tenacity

import config
from entities.extraction_function import extraction_function
from entities.llm_response import LLMResponse
from interface_adapters.llm_processor import LLMProcessor
from use_cases.prompt_templates.chat_prompt_creator import ChatPromptCreator
from langchain.chat_models import ChatOpenAI

logger = logging.getLogger(__name__)


class OpenAIProcessor(LLMProcessor):
    async def asequential_generate(self, input_text):
        pass

    def __init__(self):
        self._parser = ChatPromptCreator(llm=ChatOpenAI()).extraction_parser
        self._model = config.LLM_MODEL
        self.functions = extraction_function

    @property
    def parser(self):
        return self._parser

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(5),
        wait=tenacity.wait_random_exponential(max=30),
        retry=(tenacity.retry_if_exception_type(openai.error.OpenAIError)),
        reraise=True,
        before_sleep=tenacity.before_sleep_log(logger, logging.DEBUG)
    )
    async def agenerate_extraction(self, input_text, document_name, chunk_id):
        messages = [
            {"role": "system",
             "content": '''Given the following text, identify and extract ALL personal information details into the list'
                        of data items in the JSON schema provided of the extract_personal_info_entities function
                        Each different person should be included in a separate JSON object in the list.
                        Do not include any key-value pairs where the value is blank or absent in the text.
                        '''},

            {"role": "user",
             "content": "text: " + input_text[0]["input"] + " IMPORTANT: Remember do not! include any key-value "
                                                            "pairs where the value is blank or absent in the "
                                                            "text. ABSOLUTELY NO BLANK VALUES!"},
        ]
        response = await openai.ChatCompletion.acreate(
            model='gpt-3.5-turbo-0613',
            messages=messages,
            functions=self.functions,
            function_call='auto',
            temperature=0.4,
        )
        response_message = response["choices"][0]["message"]
        if response_message.get("function_call"):
            response_text = response_message["function_call"].arguments
            print(f'FUNCTION CALL RESULT: {response_text}')
            return LLMResponse(text=response_text,
                               finish_reason=response["choices"][0]["finish_reason"],
                               total_tokens=response["usage"]["total_tokens"])
        else:
            return None
