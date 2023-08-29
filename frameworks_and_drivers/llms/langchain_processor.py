import json

from langchain import LLMChain
from langchain.chat_models import AzureChatOpenAI

import config
from entities.llm_response import LLMResponse
from entities.personal_info_list import PersonalInfoList
from frameworks_and_drivers.classified_instructor import ClassifiedInstructor
from interface_adapters.llm_processor import LLMProcessor
from use_cases.prompt_templates.chat_prompt_creator import ChatPromptCreator


class LangchainProcessor(LLMProcessor):
    def __init__(self):
        self.llm = AzureChatOpenAI(
            openai_api_base=config.OPENAI_API_BASE,
            openai_api_type=config.OPENAI_TYPE,
            openai_api_version=config.OPENAI_API_VERSION,
            openai_api_key=config.AZURE_AI_API_KEY,
            deployment_name=config.AZURE_DEPLOYMENT_NAME,
            model_name=config.LLM_MODEL.value,
            temperature=config.TEMPERATURE,
        )
        self.prompt_creator = ChatPromptCreator(llm=self.llm)

    async def agenerate_extraction(self, input_text, document_name, chunk_id):
        # load tagger
        with open("state.json", "r") as json_file:
            value = json.load(json_file)
            toggle_status = value["ner_toggle"]

        print(toggle_status)

        text_input = input_text[0]["input"]
        print("Input: " + text_input)

        prompt = (
            self.prompt_creator.create_ner_extract_prompt(text_input)
            .format_prompt(input=text_input)
            .to_string()
        )
        print("Prompt: " + prompt)
        print()

        if toggle_status:
            chain = LLMChain(
                llm=self.llm,
                prompt=self.prompt_creator.create_ner_extract_prompt(text_input),
                verbose=True,
                tags=[f"document_name:{document_name}", f"chunk_id:{chunk_id}"],
            )
        else:
            chain = LLMChain(
                llm=self.llm,
                prompt=self.prompt_creator.create_extraction_prompt(),
                verbose=True,
                tags=[f"document_name:{document_name}", f"chunk_id:{chunk_id}"],
            )
        result = await chain.agenerate(input_text)
        generation = result.generations[0][0]
        finish_reason = None
        if generation.generation_info is not None:
            if "finish_reason" in generation.generation_info:
                finish_reason = generation.generation_info["finish_reason"]

        return LLMResponse(text=generation.text, finish_reason=finish_reason)

    async def asequential_generate(self, input_text):
        llm = AzureChatOpenAI(
            openai_api_base=config.OPENAI_API_BASE,
            openai_api_type=config.OPENAI_TYPE,
            openai_api_version=config.OPENAI_API_VERSION,
            openai_api_key=config.AZURE_AI_API_KEY,
            deployment_name=config.AZURE_DEPLOYMENT_NAME,
            model_name=config.LLM_MODEL.value,
            max_tokens=650,
            temperature=config.TEMPERATURE,
        )
        classification_chain = LLMChain(
            llm=llm,
            prompt=self.prompt_creator.create_classification_prompt(),
            verbose=True,
        )
        result = await classification_chain.apredict(input=input_text[0]["input"])
        classified_entities = self.prompt_creator.classification_parser.parse(result)
        format_instructions = ClassifiedInstructor(
            pydantic_object=PersonalInfoList
        ).get_format_instructions(contained_entities=classified_entities)

        if format_instructions is None:
            print("NO ENTITIES FOUND")
            return LLMResponse(
                text=json.dumps({"data": []}), finish_reason="No entities found"
            )
        print(f"format_instructions: {format_instructions}")

        extraction_chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_creator.create_classified_extraction_prompt(
                format_instructions
            ),
            verbose=True,
            output_parser=self.prompt_creator.extraction_parser,
        )
        result = await extraction_chain.agenerate(input_text)
        generation = result.generations[0][0]
        finish_reason = None
        if generation.generation_info is not None:
            if "finish_reason" in generation.generation_info:
                finish_reason = generation.generation_info["finish_reason"]

        return LLMResponse(text=generation.text, finish_reason=finish_reason)

    @property
    def parser(self):
        return self.prompt_creator.extraction_parser

    @property
    def retry_parser(self):
        return self.prompt_creator.extraction_fixing_parser
