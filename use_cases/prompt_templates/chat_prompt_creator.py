from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser, RetryWithErrorOutputParser

from entities.contained_entities import ContainedEntities
from entities.personal_info_list import PersonalInfoList


class ChatPromptCreator:
    def __init__(self, llm):
        self.extraction_parser = PydanticOutputParser(pydantic_object=PersonalInfoList)
        self.extraction_fixing_parser = RetryWithErrorOutputParser.from_llm(parser=self.extraction_parser, llm=llm)
        self.classification_parser = PydanticOutputParser(pydantic_object=ContainedEntities)
        self.extraction_template = '''
        Given the following text, identify and extract personal information details as per 
        the fields in the JSON schema provided including whether or not certain information is contained in the text.
        Only include data that has an identifiable person associated with it.
        Ensure the output conforms to the schema structure:

        text: ```{input}``` 

        The items in the json will be persons_full_name,date_of_birth,social_security_number,full_address,
        drivers_license_number,passport_number,medical_record_number,has_account_number,has_bank_account_pin,
        has_credit_card_security_code,has_routing_number,has_account_username_with_password,has_payment_card_number,
        has_payment_card_pin,has_expiration_date,has_email_address_with_password,has_biometric_data,
        has_medical_information,has_health_insurance_information 
        
        {format_instructions}

        IMPORTANT: Format the extracted data as a JSON instance that strictly follows the provided schema. If a 
        detail is missing from the text, do not include the corresponding JSON field key. Do not include any 
        key-value pairs where the value is blank or absent in the text. Only extract and return information that is 
        explicitly mentioned in the text. If the input text is empty or non-sensible, return an empty JSON like this: 
        {{}}'''

        self.classification_template = '''
        Given the following text, determine whether the personal information named entities mentioned in the json schema
        provided exist or not.
        
        text: ```{input}``` 
        
        {format_instructions} 
        '''

    def create_extraction_prompt(self):
        extraction_prompt = ChatPromptTemplate(
            messages=[HumanMessagePromptTemplate.from_template(self.extraction_template)],
            input_variables=['input'],
            partial_variables={'format_instructions': self.extraction_parser.get_format_instructions()},
            output_parser=self.extraction_parser)
        return extraction_prompt

    def create_classified_extraction_prompt(self, format_instructions):
        extraction_prompt = ChatPromptTemplate(
            messages=[HumanMessagePromptTemplate.from_template(self.extraction_template)],
            input_variables=['input'],
            partial_variables={'format_instructions': format_instructions},
            output_parser=self.extraction_parser)
        return extraction_prompt

    def create_classification_prompt(self):
        classification_prompt = ChatPromptTemplate(
            messages=[HumanMessagePromptTemplate.from_template(self.classification_template)],
            input_variables=['input'],
            partial_variables={'format_instructions': self.classification_parser.get_format_instructions()},
            output_parser=self.classification_parser)
        return classification_prompt
