import json
from typing import Dict

from entities.contained_entities import ContainedEntities

PYDANTIC_FORMAT_INSTRUCTIONS = "The expected format for the output is:\n{schema}"


class ClassifiedInstructor:
    def __init__(self, pydantic_object):
        self.pydantic_object = pydantic_object

    def get_format_instructions(self, contained_entities: ContainedEntities):
        schema = self.pydantic_object.schema()

        # Adjust for new model structure.
        personal_info_schema = schema["definitions"]["PersonalInfo"]

        # Remove extraneous fields.
        true_fields = {}
        for field_name, field_value in personal_info_schema["properties"].items():
            if isinstance(field_value, Dict):
                if field_name.startswith('includes_'):
                    entity_attribute = field_name
                else:
                    entity_attribute = 'has_' + field_name
                if getattr(contained_entities, entity_attribute, False):
                    true_fields[field_name] = field_value

        # Check if true_fields is empty.
        if not true_fields:
            return None
        reduced_schema = {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": true_fields
                    }
                }
            },
        }

        # Ensure json in context is well-formed with double quotes.
        schema_str = json.dumps(reduced_schema)

        return PYDANTIC_FORMAT_INSTRUCTIONS.format(schema=schema_str)
