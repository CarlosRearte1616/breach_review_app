extraction_function = [
    {
        "name": "extract_personal_info_entities",
        "description": "Extract personal information entities from a text.",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "full_name": {
                                "type": "string",
                                "description": "A Human person's complete name, usually made up of a first name, "
                                               "optional middle name, and last name. No companies or places"
                                               "(e.g. 'Kenneth Ryu Masters', 'Jin Honda')"
                            },
                            "date_of_birth": {
                                "type": "string",
                                "description": "The date a person was born, typically presented in the format "
                                               "MM-DD-YYYY. (e.g. '01-15-198', 'Feb 1 2011')"
                            },
                            "social_security_number": {
                                "type": "string",
                                "description": "A unique nine-digit number given by the U.S. government to its "
                                               "citizens and certain residents. Must be exactly 9 digits, no letters "
                                               "or special characters. No X's or 0's as placeholders. (e.g. "
                                               "'123-45-6789')"
                            },
                            "full_address": {
                                "type": "string",
                                "description": "Detailed information about where someone lives, including house "
                                               "number, street, city, state, and zip code. (e.g. '23 Main St, "
                                               "Beverly Hills, CA, 90210')"
                            },
                            "driver_license_number": {
                                "type": "string",
                                "description": "A unique combination of letters and numbers assigned to a person's "
                                               "driver's license or state ID. (e.g. 'D1234567')"
                            },
                            "passport_number": {
                                "type": "string",
                                "description": "The distinctive series of letters and numbers on a passport. (e.g. "
                                               "'567029134')"
                            },
                            "medical_record_number": {
                                "type": "string",
                                "description": "The specific number given to a patient's health record at a medical "
                                               "facility. (e.g. 'MRN12345')"
                            },
                            "account_number": {
                                "type": "string",
                                "description": "A distinct series of numbers that identify an individual account, "
                                               "like a bank account. (e.g. '1234567890')"
                            },
                            "account_pin": {
                                "type": "string",
                                "description": "A 4-6 digit number or code that verifies a user when accessing an "
                                               "account. (e.g. '1234')"
                            },
                            "security_code": {
                                "type": "string",
                                "description": "The three or four-digit number on the back of a credit card used for "
                                               "validation. (e.g. '123')"
                            },
                            "routing_number": {
                                "type": "string",
                                "description": "A unique nine-digit number identifying a U.S. financial institution "
                                               "in transactions. (e.g. '1234567890')"
                            },
                            "security_password": {
                                "type": "string",
                                "description": "A mix of characters, including letters, numbers, and symbols, used to "
                                               "validate a user on digital platforms. (e.g. 'password')"
                            },
                            "payment_card_number": {
                                "type": "string",
                                "description": "The series of numbers on a credit or debit card that identify the "
                                               "card and the issuing bank. (e.g. '1111-2222-3333-4444')"
                            },
                            "payment_card_pin": {
                                "type": "string",
                                "description": "A secret number needed to approve a transaction on a payment card. ("
                                               "e.g. '4321')"
                            },
                            "expiration_date": {
                                "type": "string",
                                "description": "The month and year (MM/YY) when something, like a credit card or "
                                               "passport, is no longer valid. (e.g. '01/25')"
                            },
                            "username_with_password": {
                                "type": "string",
                                "description": "A unique identifier (username) paired with a secret character string "
                                               "(password) for accessing digital services. (e.g. 'johndoe/password')"
                            },
                            "email_address_with_password": {
                                "type": "string",
                                "description": "An email identifier matched with a secret character string (password) "
                                               "used to access an email account. (e.g. 'johndoe@example.com/password')"
                            },
                            "includes_biometric_data": {
                                "type": "string",
                                "description": "Indicates whether the text includes distinctive physical or "
                                               "behavioral traits of a person, like fingerprints or face shape, "
                                               "used for identification or access. (e.g. 'Yes', 'No')"
                            },
                            "includes_has_medical_information": {
                                "type": "string",
                                "description": "Indicates whether the text includes any health-related data "
                                               "associated with an identifiable person. It covers health history, "
                                               "current conditions, treatments, test results, prescriptions, "
                                               "immunizations, and doctor/clinic information. (e.g. 'Yes', 'No')"
                            },
                            "includes_health_insurance_information": {
                                "type": "string",
                                "description": "Indicates whether the text includes information about a person's "
                                               "health insurance information. It includes the insurance company, "
                                               "policy type, benefits plan name, various identification numbers (like "
                                               "account, patient, beneficiary, subscriber member, claim), and details "
                                               "on what the policy covers. (e.g. 'Yes', 'No')"
                            }
                        },
                        "required": ["full_name"]
                    }
                }
            }
        }
    },
]
