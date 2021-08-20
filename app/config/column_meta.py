import pandas as pd
from app.controllers.data_types import *
from app.config.config import Config

TYPE_PATTERNS = {
    "ZIP": {
        "patterns": ["^\d{5}(-\d{4})?$|^\d{5}(-\d{4})?$"],
        "class": Zip
    },
    "CC_NUMBER": {
        "patterns": [
            "^4[0-9]{12}(?:[0-9]{3})?$",
            "^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
            "^3[47][0-9]{13}$",
            "^6(?:011|5[0-9]{2})[0-9]{12}$",
            "^3(?:0[0-5]|[68][0-9])[0-9]{11}$",
            "^(?:2131|1800|35\d{3})\d{11}$"
        ],
        "subTypes": [
            "Visa",
            "MasterCard",
            "American Express",
            "Discover",
            "Diners Club",
            "JCB"
        ],
        "class": CCNumber
    },
    "BOOLEAN": {
        "patterns": [
            "^(TRUE|true|T|t|True|1|FALSE|false|F|f|False|0)$"
        ],
        "class": Boolean
    },
    "EMAIL": {
        "patterns": [
            "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
        ],
        "class": Email
    },
    "ENUM": {
        "patterns": [
            "^\d*$"
        ],
        "class": Enum
    },
    "GENDER": {
        "patterns": [
            "^(MALE|male|M|m|Male|FEMALE|female|F|f|Female|OTHER|other|O|o|Other|UNKNOWN|unknown|U|u|Unknown)$"
        ],
        "class": Gender
    },
    "INTEGER": {
        "patterns": [
            "^\d*$"
        ],
        "class": Integer
    },
    "IPADDRESS": {
        "patterns": [
            "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        ],
        "class": IPAddress
    },
    "NUMBER": {
        "patterns": [
            "^\d*(\.\d+)?$"
        ],
        "class": Number
    },
    "ADDRESS": {
        "patterns": [
            ".*"
        ],
        "class": Address
    },
    "CITY": {
        "patterns": [
            ".*"
        ],
        "class": City
    },
    "STATE": {
        "patterns": [
            ".*"
        ],
        "class": State
    },
    "COUNTRY": {
        "patterns": [
            ".*"
        ],
        "class": Country
    },
    "FIRSTNAME": {
        "patterns": [
            ".*"
        ],
        "class": FirstName
    },
    "LASTNAME": {
        "patterns": [
            ".*"
        ],
        "class": LastName
    },
    "STRING": {
        "patterns": [
            ".*"
        ],
        "class": String
    },
    "PHONENUMBER": {
        "patterns": [
            "^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$"
        ],
        "class": PhoneNumber
    },
    "SSNUMBER": {
        "patterns": [
            "^\d{3}-?\d{2}-?\d{4}$"
        ],
        "class": SSNumber
    },
    "CCNUMBER": {
        "patterns": [
            "^4[0-9]{12}(?:[0-9]{3})?$",
            "^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
            "^3[47][0-9]{13}$",
            "^6(?:011|5[0-9]{2})[0-9]{12}$",
            "^3(?:0[0-5]|[68][0-9])[0-9]{11}$",
            "^(?:2131|1800|35\d{3})\d{11}$"
        ],
        "subTypes": [
            "Visa",
            "MasterCard",
            "American Express",
            "Discover",
            "Diners Club",
            "JCB"
        ],
        "class": CCNumber
    },
    "DATETIME": {
        "patterns": [
            ".*"
        ],
        "class": Datetime
    }
}

SUGGESTION_CONFIG = {
    1: {
        "type": "ZIP",
        "method": "pattern",
        "value": TYPE_PATTERNS['ZIP']['patterns'],
        "class": Zip
    },
    2: {
        "type": "CCNUMBER",
        "method": "pattern",
        "value": TYPE_PATTERNS['CCNUMBER']['patterns'],
        "class": CCNumber
    },
    3: {
        "type": "SSNUMBER",
        "method": "pattern",
        "value": TYPE_PATTERNS['SSNUMBER']['patterns'],
        "class": SSNumber
    },
    4: {
        "type": "IPADDRESS",
        "method": "pattern",
        "value": TYPE_PATTERNS['IPADDRESS']['patterns'],
        "class": IPAddress
    },
    5: {
        "type": "EMAIL",
        "method": "pattern",
        "value": TYPE_PATTERNS['EMAIL']['patterns'],
        "class": Email
    },
    6: {
        "type": "BOOLEAN",
        "method": "pattern",
        "value": TYPE_PATTERNS['BOOLEAN']['patterns'],
        "class": Boolean
    },
    7: {
        "type": "PHONENUMBER",
        "method": "pattern",
        "value": TYPE_PATTERNS['PHONENUMBER']['patterns'],
        "class": PhoneNumber
    },
    8: {
        "type": "GENDER",
        "method": "pattern",
        "value": TYPE_PATTERNS['GENDER']['patterns'],
        "class": Gender
    },
    9: {
        "type": "NUMBER",
        "method": "pattern",
        "value": TYPE_PATTERNS['NUMBER']['patterns'],
        "class": Number
    },
    10: {
        "type": "INTEGER",
        "method": "pattern",
        "value": TYPE_PATTERNS['INTEGER']['patterns'],
        "class": Integer
    },
    11: {
        "type": "ENUM",
        "method": "pattern",
        "value": TYPE_PATTERNS['ENUM']['patterns'],
        "class": Enum
    },
    12: {
        "type": "FIRSTNAME",
        "method": "lookup",
        "value": set(pd.read_csv(f'{Config.DATA_PATH}/us_firstnames.txt',
                                 header=None)[0]),
        "class": FirstName
    },
    13: {
        "type": "LASTNAME",
        "method": "lookup",
        "value": set(pd.read_csv(f'{Config.DATA_PATH}/us_lastnames.txt',
                                 header=None)[0]),
        "class": LastName
    },
    20: {
        "type": "ADDRESS",
        "method": "pattern",
        "value": TYPE_PATTERNS['ADDRESS']['patterns'],
        "class": Address
    },
    15: {
        "type": "CITY",
        "method": "lookup",
        "value": set(pd.read_csv(f'{Config.DATA_PATH}/us_cities.txt',
                                 header=None)[0]),
        "class": City
    },
    17: {
        "type": "COUNTRY",
        "method": "lookup",
        "value": set(pd.read_csv(f'{Config.DATA_PATH}/countries.txt',
                                 header=None)[0]),
        "class": Country
    },
    16: {
        "type": "STATE",
        "method": "lookup",
        "value": set(pd.read_csv(f'{Config.DATA_PATH}/us_states.txt',
                                 header=None)[0]),
        "class": State
    },
    19: {
        "type": "STRING",
        "method": "pattern",
        "value": TYPE_PATTERNS['STRING']['patterns'],
        "class": String
    },
    18: {
        "type": "DATETIME",
        "method": "datetime",
        "value": "",
        "class": Datetime
    }
}
