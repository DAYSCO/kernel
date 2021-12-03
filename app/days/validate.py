import os
import pandas as pd

import idna
import re

from smartystreets_python_sdk import (StaticCredentials, exceptions, Batch,
                                      SharedCredentials, ClientBuilder)
from smartystreets_python_sdk.us_street import Lookup as StreetLookup
from smartystreets_python_sdk.us_zipcode import Lookup as ZIPCodeLookup
from smartystreets_python_sdk.us_autocomplete_pro import (
    Lookup as AutocompleteProLookup
)

from dateutil.parser import parse
from .custom_types import *
from app.util import ConnectionManager


class Validation:

    SMARTYSTREETS_AUTH_TOKEN = os.environ.get('SMARTYSTREETS_AUTH_TOKEN',
                                              'M5VB7vOR63EYUvkqQWzP')
    SMARTYSTREETS_AUTH_ID = os.environ.get(
        'SMARTYSTREETS_AUTH_ID', '5aa199f9-3d5f-f2ba-b41f-74b953b5d1d6')
    USERID = "467DAYS06449"
    KEY_ID = os.environ.get("KEY_ID", '33603386701207625')
    SMARTYSTREETS_HOSTNAME = os.environ.get("SMARTYSTREETS_HOSTNAME",
                                            "playwithmydata.com/")

    @classmethod
    def validate(cls, series, custom_type, invalid="INVALID"):
        if custom_type == "BOOLEAN":
            series = series.apply(cls.boolean, invalid=invalid)
        elif custom_type == "FULLADDRESS":
            series = cls.full_address(series, invalid=invalid)
        elif custom_type == "EMAIL":
            series = series.apply(cls.email, invalid=invalid)
        elif custom_type == "GENDER":
            series = series.apply(cls.gender, invalid=invalid)
        elif custom_type == "IPADDRESS":
            series = series.apply(cls.ip_address, invalid=invalid)
        elif custom_type == "PHONENUMBER":
            series = series.apply(cls.phone_number, invalid=invalid)
        elif custom_type == "SSNUMBER":
            series = series.apply(cls.ss_number, invalid=invalid)
        elif custom_type == "CCNUMBER":
            series = series.apply(cls.cc_number, invalid=invalid)
        elif custom_type == "DATETIME":
            series = series.apply(cls.datetime, invalid=invalid)
        return series
    
    @staticmethod
    def pattern_match(val, pattern):
        return bool(pattern.match(val.lower()))

    @classmethod
    def gender(cls, val, invalid="INVALID"):
        for pat, sval in zip(Patterns.GENDER, Patterns.GENDER_VALUES):
            if cls.pattern_match(val, re.compile(pat)):
                val.VALIDATION_META['valid'] = True
                val.gender = sval
                return val
        new_val = Gender(invalid)
        new_val.VALIDATION_META['valid'] = False
        new_val.VALIDATION_META['errors'].append("Value could not be parsed.")
        return new_val

    @classmethod
    def boolean(cls, val, invalid="INVALID"):
        for pat, sval in zip(Patterns.BOOLEAN, Patterns.BOOLEAN_VALUES):
            if cls.pattern_match(val, re.compile(pat)):
                val.VALIDATION_META['valid'] = True
                val.bool_value = sval
                return val
        new_val = Boolean(invalid)
        new_val.VALIDATION_META['valid'] = False
        new_val.VALIDATION_META['errors'].append("Value could not be parsed.")
        return new_val

    @classmethod
    def full_address(cls, series, invalid="INVALID"):
        new_series = []
        for x in cls.batch(series, 100):
            new_series.extend(
                cls.smartystreet(address_full=list(x), invalid=invalid))
        return pd.Series(new_series)

    @classmethod
    def cc_number(cls, val, invalid="INVALID"):
        if cls.luhn(val):
            for pat, sval in zip(Patterns.CCNUMBER, Patterns.CCNUMBER_VALUES):
                if cls.pattern_match(val, re.compile(pat)):
                    val.VALIDATION_META['valid'] = True
                    val.provider = sval
                    return val
            new_val = CCNumber(invalid)
            new_val.VALIDATION_META['valid'] = False
            new_val.VALIDATION_META['errors'].append(
                "Provider could not be identified.")
            return val
        else:
            new_val = CCNumber(invalid)
            new_val.VALIDATION_META['valid'] = False
            new_val.VALIDATION_META['errors'].append("Value failed checksum.")
        return new_val

    @classmethod
    def ss_number(cls, val, invalid="INVALID"):
        if cls.pattern_match(val, re.compile("|".join(Patterns.SSNUMBER))):
            digits = re.sub(r"\D", "", val)
            val.VALIDATION_META['valid'] = True
            val.area_number = digits[0:3]
            val.group_number = digits[3:5]
            val.serial_number = digits[5:10]
            return val
        else:
            new_val = SSNumber(invalid)
            new_val.VALIDATION_META['valid'] = False
            new_val.VALIDATION_META['errors'].append(
                "Value could not be parsed.")
            return new_val

    @classmethod
    def datetime(cls, val, invalid="INVALID"):
        try:
            p_val = parse(val)
        except:
            new_val = Datetime(invalid)
            new_val.VALIDATION_META['valid'] = False
            new_val.VALIDATION_META['errors'].append(
                "Value could not be parsed.")
            return new_val
        val.VALIDATION_META['valid'] = True
        val.weekday = p_val.strftime("%A")
        val.weekday_abbrev = p_val.strftime("%a")
        val.weekday_number = p_val.strftime("%w")
        val.day_of_month = p_val.strftime("%d")
        val.month_name = p_val.strftime("%B")
        val.month_name_abbrev = p_val.strftime("%b")
        val.month_number = p_val.strftime("%m")
        val.year = p_val.strftime("%Y")
        val.year_abbrev = p_val.strftime("%y")
        val.hour = p_val.strftime("%H")
        val.hour_12 = p_val.strftime("%I")
        val.am_pm = p_val.strftime("%p")
        val.minute = p_val.strftime("%M")
        val.second = p_val.strftime("%S")
        val.microsecond = p_val.strftime("%f")
        val.utc_offset = p_val.strftime("%z")
        val.timezone = p_val.strftime("%Z")
        return val

    @classmethod
    def ip_address(cls, val, invalid="INVALID"):
        if cls.pattern_match(val, re.compile("|".join(Patterns.IPADDRESS))):
            parts = val.split(".")
            val.VALIDATION_META['valid'] = True
            val.network_part = ".".join(parts[0:1])
            val.host_part = ".".join(parts[2:3])
            return val
        else:
            new_val = IPAddress(invalid)
            new_val.VALIDATION_META['valid'] = False
            new_val.VALIDATION_META['errors'].append(
                "Value could not be parsed.")
            return new_val

    @classmethod
    def phone_number(cls, val, invalid="INVALID"):
        if cls.pattern_match(val, re.compile("|".join(Patterns.PHONENUMBER))):
            digits = re.sub(r"\D", "", val)
            val.VALIDATION_META['valid'] = True
            if len(digits) > 10:
                val.country_code = digits[0:len(digits)-10]
            val.area_code = digits[-10:-7]
            val.exchange = digits[-7:-4]
            val.line_number = digits[-4:]
            return val
        else:
            new_val = PhoneNumber(invalid)
            new_val.VALIDATION_META['valid'] = False
            new_val.VALIDATION_META['errors'].append(
                "Value could not be parsed.")
            return new_val

    @classmethod
    def email(cls, val, invalid="INVALID"):
        if cls.pattern_match(val, re.compile("|".join(Patterns.EMAIL))):
            parts = val.split("@")
            if cls.email_domain_validation(parts[1]):
                val.VALIDATION_META['valid'] = True
                val.local_part = parts[0]
                val.domain = parts[1]
            else:
                new_val = Email(invalid)
                new_val.VALIDATION_META['valid'] = False
                new_val.VALIDATION_META['errors'].append(
                    "Domain could not be validated.")
                return new_val
        else:
            new_val = Email(invalid)
            new_val.VALIDATION_META['valid'] = False
            new_val.VALIDATION_META['errors'].append(
                "Value could not be parsed.")
            return new_val
        return val

    @staticmethod
    def luhn(cc_number):
        try:
            digits = re.sub(r"\D", "", cc_number)
            _ = list(digits)
            last = int(_.pop(-1))
            _ = _[::-1]
            _ = [x if i % 2 != 0 else str(int(x) * 2) for i, x in enumerate(_)]
            _ = [x if int(x) <= 9 else str(int(x) - 9) for x in _]
            s = sum([int(x) for x in _])
            return (s + last) % 10 == 0
        except:
            return False

    @staticmethod
    def email_domain_validation(domain):
        if len(domain) == 0:
            return False
        try:
            domain = idna.uts46_remap(domain, std3_rules=False,
                                      transitional=False)
        except Exception:
            return False
        if domain.endswith("."):
            return False
        if domain.startswith("."):
            return False
        if ".." in domain:
            return False
        try:
            ascii_domain = idna.encode(domain, uts46=False).decode("ascii")
        except idna.IDNAError:
            return False
        try:
            idna.decode(ascii_domain.encode('ascii'))
        except idna.IDNAError:
            return False
        domain_max_length = 255
        if len(ascii_domain) > domain_max_length:
            return False
        text_hostname = r'(?:(?:[a-zA-Z0-9][a-zA-Z0-9\-]*)?[a-zA-Z0-9])'
        dot_atom_text = text_hostname + r'(?:\.' + text_hostname + r')*'
        m = re.match(dot_atom_text + "\\Z", ascii_domain)
        if not m:
            return False
        if "." not in ascii_domain:
            return False
        if not re.search(r"[A-Za-z]\Z", ascii_domain):
            return False
        return True

    @classmethod
    def smartystreet(cls, address_full=[], invalid="INVALID"):
        credentials = StaticCredentials(cls.SMARTYSTREETS_AUTH_ID,
                                        cls.SMARTYSTREETS_AUTH_TOKEN)
        client = ClientBuilder(credentials).build_us_street_api_client()
        batch = Batch()
        results = []
        for x in address_full:
            batch.add(StreetLookup(x))
        try:
            client.send_batch(batch)
        except exceptions.SmartyException as err:
            print(err)
            raise err

        for i, lookup in enumerate(batch):
            candidates = lookup.result
            if len(candidates) == 0:
                r_ser = FullAddress(invalid)
            else:
                delivery_line_1 = candidates[0].delivery_line_1 or ''
                delivery_line_2 = candidates[0].delivery_line_2 or ''
                delivery_last_line = candidates[0].last_line or ''
                address_details = f"{delivery_line_1} {delivery_line_2 + ' ' if delivery_line_2 else ''}{delivery_last_line}"
                r_ser = FullAddress(address_details)
            results.append(r_ser)
        ConnectionManager(client.sender).close()
        return results

    @classmethod
    def smartystreet_zip_code(cls, zipcode=[], invalid="INVALID"):
        credentials = StaticCredentials(cls.SMARTYSTREETS_AUTH_ID,
                                        cls.SMARTYSTREETS_AUTH_TOKEN)
        client = ClientBuilder(credentials).build_us_zipcode_api_client()
        batch = Batch()
        results = pd.Series([], dtype="string")
        for i, zip_code in enumerate(zipcode):
            batch.add(ZIPCodeLookup())
            batch[i].zipcode = zip_code
        try:
            client.send_batch(batch)
        except exceptions.SmartyException as err:
            print(err)
            raise err
        for i, lookup in enumerate(batch):
            candidates = lookup.result
            try:
                value = candidates.zipcodes[0].zipcode
            except IndexError:
                value = invalid
            r_ser = pd.Series([value])
            results = results.append(r_ser, ignore_index=True)
        ConnectionManager(client.sender).close()
        return results

    @staticmethod
    def batch(iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

    @classmethod
    def smartystreet_auto_complete(cls, address_full=[], invalid="INVALID"):
        credentials = SharedCredentials(cls.KEY_ID, cls.SMARTYSTREETS_HOSTNAME)
        client = ClientBuilder(credentials).with_licenses(
            ["us-autocomplete-pro-cloud"]
        ).build_us_autocomplete_pro_api_client()
        lookup = AutocompleteProLookup(address_full[0])

        client.send(lookup)
        results = []
        for suggestion in lookup.result:
            address = suggestion.street_line
            if suggestion.secondary:
                address += f" {suggestion.secondary}"
            address += (f", {suggestion.city}, {suggestion.state} "
                        f"{suggestion.zipcode}")
            results.append(address)

        return results

    @classmethod
    def smartystreet_us_street(cls, address='', address2='', city='', state='',
                               zip_code=''):

        credentials = StaticCredentials(cls.SMARTYSTREETS_AUTH_ID,
                                        cls.SMARTYSTREETS_AUTH_TOKEN)
        client = ClientBuilder(credentials).with_licenses(
            ["us-standard-cloud"]).build_us_street_api_client()

        lookup = StreetLookup(
            street=address,
            street2=address2,
            city=city,
            state=state,
            zipcode=zip_code,
            candidates=5,
            match="invalid"
        )

        try:
            client.send_lookup(lookup)
        except exceptions.SmartyException as err:
            print(err)
            return

        results = []

        for candidate in lookup.result:
            delivery_line_1 = candidate.delivery_line_1 or ''
            delivery_line_2 = candidate.delivery_line_2 or ''
            delivery_last_line = candidate.last_line or ''
            address_details = (
                f"{delivery_line_1} "
                f"{delivery_line_2 + ' ' if delivery_line_2 else ''}"
                f"{delivery_last_line}"
            )
            results.append(address_details)

        return results
