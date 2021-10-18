from dateutil.parser import parse

DEFAULT_META = {
  "valid": None,
  "errors": []
}


class FirstName(str):
    VALIDATION_META = DEFAULT_META


class LastName(str):
    VALIDATION_META = DEFAULT_META


class Boolean(str):
    VALIDATION_META = DEFAULT_META


class Address(str):
    VALIDATION_META = DEFAULT_META


class City(str):
    VALIDATION_META = DEFAULT_META


class State(str):
    VALIDATION_META = DEFAULT_META


class Zip(str):
    VALIDATION_META = DEFAULT_META


class Country(str):
    VALIDATION_META = DEFAULT_META


class Email(str):
    VALIDATION_META = DEFAULT_META


class Enum(str):
    VALIDATION_META = DEFAULT_META


class Gender(str):
    VALIDATION_META = DEFAULT_META


class Integer(str):
    VALIDATION_META = DEFAULT_META


class IPAddress(str):
    VALIDATION_META = DEFAULT_META


class Number(str):
    VALIDATION_META = DEFAULT_META


class PhoneNumber(str):
    VALIDATION_META = DEFAULT_META


class String(str):
    VALIDATION_META = DEFAULT_META


class CCNumber(str):
    VALIDATION_META = DEFAULT_META


class SSNumber(str):
    VALIDATION_META = DEFAULT_META


class Datetime(str):
    VALIDATION_META = DEFAULT_META
    dt_obj = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        try:
            self.dt_obj = parse(self)
            self.VALIDATION_META['valid'] = True
        except Exception as e:
            self.VALIDATION_META['valid'] = False
            self.VALIDATION_META['errors'].append(str(e))