
from app.config.column_meta import TYPE_PATTERNS
from app.handler.validator import Validator

VALIDATION_CONFIG = {
        "BOOLEAN": {
            "patterns": TYPE_PATTERNS['BOOLEAN']
        },
        "ADDRESS": {
            "patterns": TYPE_PATTERNS['ADDRESS'],
            "extended_function": Validator.address
        },
        "CITY": {
            "patterns": TYPE_PATTERNS['CITY']
        },
        "COUNTRY": {
            "patterns": TYPE_PATTERNS['COUNTRY']
        },
        "EMAIL": {
            "patterns": TYPE_PATTERNS['EMAIL'],
            "extended_function": Validator.validate_email
        },
        "ENUM": {
            "patterns": TYPE_PATTERNS['ENUM']
        },
        "GENDER": {
            "patterns": TYPE_PATTERNS['GENDER']
        },
        "INTEGER": {
            "patterns": TYPE_PATTERNS['INTEGER']
        },
        "IPADDRESS": {
            "patterns": TYPE_PATTERNS['IPADDRESS']
        },
        "NUMBER": {
            "patterns": TYPE_PATTERNS['NUMBER']
        },
        "FIRSTNAME": {
            "patterns": TYPE_PATTERNS['FIRSTNAME']
        },
        "LASTNAME": {
            "patterns": TYPE_PATTERNS['LASTNAME']
        },
        "PHONENUMBER": {
            "patterns": TYPE_PATTERNS['PHONENUMBER']
        },
        "SSNUMBER": {
            "patterns": TYPE_PATTERNS['ZIP']
        },
        "STATE": {
            "patterns": TYPE_PATTERNS['STATE']
        },
        "STRING": {
            "patterns": TYPE_PATTERNS['STRING']
        },
        "ZIP": {
            "patterns": TYPE_PATTERNS['ZIP'],
            "extended_function": Validator.zip_code
        },
        "CCNUMBER": {
            "patterns": TYPE_PATTERNS['CCNUMBER'],
            "extended_function": Validator.credit_card
        }
}