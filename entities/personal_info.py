import re
from typing import Optional, Dict

from pydantic import BaseModel

from util.regex_utils import could_be_address, could_be_ssn, could_be_name, is_drivers_license, \
    is_medical_record_number, is_date_of_birth


def sanitize_object(obj):
    pattern = re.compile(r'XXX-XX-\d{4}')  # For pattern XXX-XX-(Any four digit combination)
    # create empty PersonalInfo object to capture sanitized values
    replaced_info = PersonalInfo()
    for field_name, field_info in obj.model_fields.items():
        current_value = obj.dict(by_alias=False).get(field_name)
        if isinstance(current_value, str):
            if field_name == 'persons_full_name':
                replaced_info.__setattr__(field_name, current_value)
            if clear_value_if_field_invalid(current_value, field_name, obj):
                replaced_info.__setattr__(field_name, current_value)
            if (
                    field_info.examples and current_value in field_info.examples or
                    current_value.lower() in {'na', 'n/a', 'no', 'none', 'not found', 'unknown', 'not required',
                                              'xx'} or
                    '1234' in current_value or
                    'XXX-XX-XXXX' in current_value or
                    'xx' in current_value or
                    '[client name]' in current_value or
                    re.match(pattern, current_value)
            ):
                setattr(obj, field_name, "")
                replaced_info.__setattr__(field_name, current_value)

        elif current_value is None or current_value is False:
            setattr(obj, field_name, "")
            replaced_info.__setattr__(field_name, current_value)

    return obj, replaced_info


def clear_value_if_field_invalid(current_value, field_name, obj):
    if field_name == 'persons_full_name':
        if not could_be_name(current_value):
            setattr(obj, field_name, "")
    if field_name == 'date_of_birth':
        if not is_date_of_birth(current_value):
            setattr(obj, field_name, "")
    if field_name == 'full_address':
        if not could_be_address(current_value):
            setattr(obj, field_name, "")
    if field_name == 'social_security_number':
        if not could_be_ssn(current_value):
            setattr(obj, field_name, "")
    if field_name == 'drivers_license_number':
        if not is_drivers_license(current_value):
            setattr(obj, field_name, "")
    if field_name == 'medical_record_number':
        if not is_medical_record_number(current_value):
            setattr(obj, field_name, "")
    if current_value != getattr(obj, field_name):
        return True
    return False


def is_junk_value(obj, value):
    pattern = re.compile(r'XXX-XX-\d{4}')  # For pattern XXX-XX-(Any four digit combination)
    special_values = {'na', 'n/a', 'no', 'none', 'not found', 'unknown', 'not required', 'xx', 'False'}

    # Check if value is None or empty
    if value is None:
        return True

    # Convert to string and then check for special values and pattern
    str_value = str(value)  # Converts value to string

    if (
            str_value.lower() in special_values or  # Matches given set of strings
            '1234' in str_value or  # Contains 1234 anywhere in the string
            'XXX-XX-XXXX' in str_value or  # Contains XXX-XX-XXXX anywhere in the string
            re.match(pattern, str_value)  # Matches pattern XXX-XX-(Any four digit combination)
    ):
        return True
    elif value is False or value is None:
        return True

    # Check if value matches any of the examples in the Pydantic model
    for field in obj.model_fields.values():
        examples = field.examples
        if examples and str_value in examples:
            return True

    return False


class PersonalInfo(BaseModel):
    persons_full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    social_security_number: Optional[str] = None
    full_address: Optional[str] = None
    drivers_license_number: Optional[str] = None
    passport_number: Optional[str] = None
    medical_record_number: Optional[str] = None
    has_account_number: Optional[bool] = False
    has_bank_account_pin: Optional[bool] = False
    has_credit_card_security_code: Optional[bool] = False
    has_routing_number: Optional[bool] = False
    has_account_username_with_password: Optional[bool] = False
    has_payment_card_number: Optional[bool] = False
    has_payment_card_pin: Optional[bool] = False
    has_expiration_date: Optional[bool] = False
    has_email_address_with_password: Optional[bool] = False
    has_biometric_data: Optional[bool] = False
    has_medical_information: Optional[bool] = False
    has_health_insurance_information: Optional[bool] = False

    def is_potential_hallucination(self) -> bool:
        print("Checking if hallucination is present")
        for name, field_info in self.model_fields.items():
            if field_info.examples and self.__dict__[name] in field_info.examples:
                if self.__dict__[name] not in ["Yes", "No", True, False]:
                    return True
        return False

    @classmethod
    def from_dict(cls, data: Dict) -> 'PersonalInfo':
        return cls(**data)


class PersonalInfoWithChunkSource:
    def __init__(self, personal_info: PersonalInfo, chunk_source: str):
        self.info = personal_info
        self.source = chunk_source
