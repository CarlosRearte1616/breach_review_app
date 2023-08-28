from typing import Optional, Dict
from pydantic import BaseModel, Field


class ContainedEntities(BaseModel):
    has_full_name: Optional[bool] = Field(
        description="Indicates whether the text contains a person's complete name.",
    )
    has_date_of_birth: Optional[bool] = Field(
        description="Indicates whether the text contains a person's date of birth.",
    )
    has_social_security_number: Optional[bool] = Field(
        description="Indicates whether the text contains a person's social security number.",
    )
    has_full_address: Optional[bool] = Field(
        description="Indicates whether the text contains a person's full address.",
    )
    has_driver_license_number: Optional[bool] = Field(
        description="Indicates whether the text contains a person's driver's license number.",
    )
    has_passport_number: Optional[bool] = Field(
        description="Indicates whether the text contains a person's passport number.",
    )
    has_medical_record_number: Optional[bool] = Field(
        description="Indicates whether the text contains a person's medical record number.",
    )
    has_account_number: Optional[bool] = Field(
        description="Indicates whether the text contains a person's account number.",
    )
    has_account_pin: Optional[bool] = Field(
        description="Indicates whether the text contains a person's account PIN.",
    )
    has_security_code: Optional[bool] = Field(
        description="Indicates whether the text contains a security code.",
    )
    has_routing_number: Optional[bool] = Field(
        description="Indicates whether the text contains a routing number.",
    )
    has_security_password: Optional[bool] = Field(
        description="Indicates whether the text contains a security password.",
    )
    has_payment_card_number: Optional[bool] = Field(
        description="Indicates whether the text contains a payment card number.",
    )
    has_payment_card_pin: Optional[bool] = Field(
        description="Indicates whether the text contains a payment card PIN.",
    )
    has_expiration_date: Optional[bool] = Field(
        description="Indicates whether the text contains an expiration date.",
    )
    has_username_with_password: Optional[bool] = Field(
        description="Indicates whether the text contains a username with password.",
    )
    has_email_address_with_password: Optional[bool] = Field(
        description="Indicates whether the text contains an email address with password.",
    )
    has_includes_biometric_data: Optional[bool] = Field(
        description="Indicates whether the text contains biometric data.",
    )
    includes_biometric_data: Optional[bool] = Field(
        description="Does text include distinctive physical or behavior traits of a person, like fingerprints or face "
                    "shape, used for identification or access?",
    )
    includes_has_medical_information: Optional[bool] = Field(
        description="Does text include any health-related data associated with an identifiable person?. It covers "
                    "health history, current conditions, treatments, test results, prescriptions, immunizations, "
                    "and doctor/clinic information.",
    )
    includes_health_insurance_information: Optional[bool] = Field(
        description="Does text include information about a person's health insurance information?. It includes the "
                    "insurance company, policy type, benefits plan name, various identification numbers (like "
                    "account, patient, beneficiary, subscriber member, claim), and details on what the policy covers.",
    )
