class FirstName(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}


class LastName(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}


class FullName(str):
    '''
    raw = "Rev. Dr. Martin Luther King Jr."
    prefixes = ["Rev.", "Dr."]
    given_names = ["Martin", "Luther"]
    family_name = "King"
    suffixes = ["Jr."]
    '''
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}
        self.prefixes = list()
        self.given_names = list()
        self.family_name = str()
        self.suffixes = list()


class Boolean(str):
    '''
    raw = "TRUE"
    bool_value = True
    '''
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}
        self.bool_value = bool()


class StreetAddress(str):
    '''
    raw = ""
    urbanization = None
    primary_number = None
    street_name = None
    street_predirection = None
    street_postdirection = None
    street_suffix = None
    secondary_number = None
    secondary_designator = None
    extra_secondary_number = None
    extra_secondary_designator = None
    pmb_designator = None
    pmb_number = None
    '''
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}
        self.urbanization = str()
        self.primary_number = str()
        self.street_name = str()
        self.street_predirection = str()
        self.street_postdirection = str()
        self.street_suffix = str()
        self.secondary_number = str()
        self.secondary_designator = str()
        self.extra_secondary_number = str()
        self.extra_secondary_designator = str()
        self.pmb_designator = str()
        self.pmb_number = str()


class FullAddress(str):
    '''
    raw = ""
    input_id = None
    input_index = None
    candidate_index = None
    addressee = None
    delivery_line_1 = None
    delivery_line_2 = None
    last_line = None
    delivery_point_barcode = None
    urbanization = None
    primary_number = None
    street_name = None
    street_predirection = None
    street_postdirection = None
    street_suffix = None
    secondary_number = None
    secondary_designator = None
    extra_secondary_number = None
    extra_secondary_designator = None
    pmb_designator = None
    pmb_number = None
    city_name = None
    default_city_name = None
    state_abbreviation = None
    zipcode = None
    plus4_code = None
    delivery_point = None
    delivery_point_check_digit = None
    record_type = None
    zip_type = None
    county_fips = None
    county_name = None
    ews_match = None
    carrier_route = None
    congressional_district = None
    building_default_indicator = None
    rdi = None
    elot_sequence = None
    elot_sort = None
    latitude = None
    longitude = None
    coordinate_license = None
    precision = None
    time_zone = None
    utc_offset = None
    dst = None
    '''
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}
        self.input_id = str()
        self.input_index = str()
        self.candidate_index = str()
        self.addressee = str()
        self.delivery_line_1 = str()
        self.delivery_line_2 = str()
        self.last_line = str()
        self.delivery_point_barcode = str()
        self.urbanization = str()
        self.primary_number = str()
        self.street_name = str()
        self.street_predirection = str()
        self.street_postdirection = str()
        self.street_suffix = str()
        self.secondary_number = str()
        self.secondary_designator = str()
        self.extra_secondary_number = str()
        self.extra_secondary_designator = str()
        self.pmb_designator = str()
        self.pmb_number = str()
        self.city_name = str()
        self.default_city_name = str()
        self.state_abbreviation = str()
        self.zipcode = str()
        self.plus4_code = str()
        self.delivery_point = str()
        self.delivery_point_check_digit = str()
        self.record_type = str()
        self.zip_type = str()
        self.county_fips = str()
        self.county_name = str()
        self.ews_match = str()
        self.carrier_route = str()
        self.congressional_district = str()
        self.building_default_indicator = str()
        self.rdi = str()
        self.elot_sequence = str()
        self.elot_sort = str()
        self.latitude = str()
        self.longitude = str()
        self.coordinate_license = str()
        self.precision = str()
        self.time_zone = str()
        self.utc_offset = str()
        self.dst = str()


class City(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}


class State(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}


class Zip(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}


class Country(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}


class Email(str):
    '''
    raw = "name123@gmail.com"
    local_part = "name123"
    domain = "gmail.com"
    '''
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}
        self.local_part = str()
        self.domain = str()


class Enum(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}


class Gender(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}
        self.gender = str()


class Integer(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}


class IPAddress(str):
    '''
    raw = "101.010.01.01"
    network_part = "101.010"
    host_part = "01.01"
    '''
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}
        self.network_part = str()
        self.host_part = str()


class Number(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}


class PhoneNumber(str):
    '''
    raw = "+1 (123) 456 7890"
    country_code = "1"
    area_code = "123"
    exchange = "456"
    line_number = "7890"
    '''
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}
        self.country_code = str()
        self.area_code = str()
        self.exchange = str()
        self.line_number = str()


class String(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}


class CCNumber(str):
    '''
    raw = "378282246310005"
    provider = "American Express"
    '''
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}
        self.provider = str()


class SSNumber(str):
    '''
    raw = "123-45-6789"
    area_number = "123"
    group_number = "45"
    serial_number = "6789"
    '''
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}
        self.area_number = str()
        self.group_number = str()
        self.serial_number = str()


class Datetime(str):
    '''
    raw = "12/31/2001 00:00:00000"
    weekday = "Monday"
    weekday_abbrev = "Mon"
    weekday_number = "1"
    day_of_month = "31"
    month_name = "December"
    month_name_abbrev = "Dec"
    month_number = "12"
    year = "2001"
    year_abbrev = "01"
    hour = "00"
    hour_12 = "12"
    am_pm = "AM"
    minute = "00"
    second = "00"
    microsecond = "000000"
    utc_offset = "+0000"
    timezone = None
    '''
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.VALIDATION_META = {"valid": None, "errors": list()}
        self.weekday = str()
        self.weekday_abbrev = str()
        self.weekday_number = str()
        self.day_of_month = str()
        self.month_name = str()
        self.month_name_abbrev = str()
        self.month_number = str()
        self.year = str()
        self.year_abbrev = str()
        self.hour = str()
        self.hour_12 = str()
        self.am_pm = str()
        self.minute = str()
        self.second = str()
        self.microsecond = str()
        self.utc_offset = str()
        self.timezone = str()


class Patterns:
    BOOLEAN = [ r"^(true|t|1)$", r"^(false|f|0)$" ]
    BOOLEAN_VALUES = [ True, False ]
    CCNUMBER = [
        r"^4[0-9]{12}(?:[0-9]{3})?$",
        r"^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
        r"^3[47][0-9]{13}$",
        r"^6(?:011|5[0-9]{2})[0-9]{12}$",
        r"^3(?:0[0-5]|[68][0-9])[0-9]{11}$",
        r"^(?:2131|1800|35\d{3})\d{11}$" ]
    CCNUMBER_VALUES = [
        "Visa",
        "MasterCard",
        "American Express",
        "Discover",
        "Diners Club",
        "JCB" ]
    EMAIL = [ r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)*$" ]
    GENDER = [ r"^(male|m)$", r"^(female|f)$", r"^(other|o|unknown|u)$" ]
    GENDER_VALUES = [
        "MALE",
        "FEMALE",
        "OTHER/UNKNOWN" ]
    INTEGER = [ r"^\d*$" ]
    IPADDRESS = [ r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$" ]
    NUMBER = [ r"^\(?-?(\d{1,3},?(\d{3},?)*)?\.?\d*\)?$" ]
    PHONENUMBER = [ r"^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$" ]
    SSNUMBER = [ r"^\d{3}-?\d{2}-?\d{4}$" ]
    STREETADDRESS = [ r"^(#?\d+-?\d*|ap|p\.?o\.?)(#?\d*(\.|,)? ?|[-a-z]*(\.|,)? ?)*$" ]
    ZIP = [ r"^\d{5}(-\d{4})?$|^\d{5}(-\d{4})?$" ]