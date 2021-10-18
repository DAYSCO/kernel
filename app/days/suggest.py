import os
import re
import pandas as pd
from collections import Counter
from dateutil.parser import parse
from .custom_types import *
from app.config.config import Config

DATA_PATH = os.environ.get("DATA_PATH", Config.DATA_PATH)
CITY_DATA = set(pd.read_csv(f"{DATA_PATH}/us_cities.txt", header=None)
                [0].apply(lambda x: re.sub(r"(\s|\.|-|')", "", x.lower())))
STATE_DATA = set(pd.read_csv(f"{DATA_PATH}/us_states.txt", header=None)
                 [0].apply(lambda x: re.sub(r"(\s|\.|-|')", "", x.lower())))
FIRSTNAME_DATA = set(pd.read_csv(f"{DATA_PATH}/us_firstnames.txt", header=None)
                     [0].apply(lambda x: re.sub(r"(\s|\.|-|')", "",
                                                x.lower())))
LASTNAME_DATA = set(pd.read_csv(f"{DATA_PATH}/us_lastnames.txt", header=None)
                    [0].apply(lambda x: re.sub(r"(\s|\.|-|')", "", x.lower())))

COUNTRY_DATA = set(pd.read_csv(f"{DATA_PATH}/countries.txt", header=None)
                   [0].apply(lambda x: re.sub(r"(\s|\.|-|')", "", x.lower())))


class Suggestion:
    THRESHOLD = 0.5

    @classmethod
    def tests(cls):
        return [
            (cls.zip, "ZIP", Zip),
            (cls.cc_number, "CCNUMBER", CCNumber),
            (cls.ss_number, "SSNUMBER", SSNumber),
            (cls.ip_address, "IPADDRESS", IPAddress),
            (cls.email, "EMAIL", Email),
            (cls.boolean, "BOOLEAN", Boolean),
            (cls.phone_number, "PHONENUMBER", PhoneNumber),
            (cls.gender, "GENDER", Gender),
            (cls.enum, "ENUM", Enum),
            (cls.number, "NUMBER", Number),
            (cls.integer, "INTEGER", Integer),
            (cls.datetime, "DATETIME", Datetime),
            (cls.street_address, "STREETADDRESS", StreetAddress),
            (cls.full_address, "FULLADDRESS", FullAddress),
            (cls.first_name, "FIRSTNAME", FirstName),
            (cls.last_name, "LASTNAME", LastName),
            (cls.country, "COUNTRY", Country),
            (cls.state, "STATE", State),
            (cls.city, "CITY", City)
        ]

    @classmethod
    def suggest_type(cls, series):
        for test_func, custom_type, days_type in cls.tests():
            if test_func(series):
                return pd.Series([days_type(x) for _, x in
                                  series.items()]), custom_type
        return pd.Series([String(x) for _, x in series.items()]), "STRING"

    @staticmethod
    def sample(series):
        row_count = len(series)
        series = series.dropna().apply(lambda x: x.lower())
        if row_count < 100:
            return series
        elif row_count < 10000:
            return series.sample(row_count // 10, replace=True)
        else:
            return series.sample(1000, replace=True)

    @staticmethod
    def unordered_pattern_match(sample, patterns, threshold):
        pass

    @staticmethod
    def pattern_match(sample, pattern, threshold):
        row_count = len(sample)
        result = sample.str.contains(pattern)
        true_values = result.value_counts().get(True, 0)
        if true_values >= (row_count * threshold):
            return True
        else:
            return False

    @staticmethod
    def lookup_match(sample, data, threshold):
        row_count = len(sample)
        sample = sample.apply(lambda x: re.sub(r"(\s|\.|-|')", "", x))
        result = list(sample)
        true_values = 0
        sub_data = data.intersection(set(sample))
        count_values = Counter(sub_data)
        for value in result:
            true_values += count_values.get(value, 0)
        if true_values >= (row_count * threshold):
            return True
        else:
            return False

    @classmethod
    def boolean(cls, series):
        return cls.pattern_match(
            cls.sample(series), "|".join(Patterns.BOOLEAN), cls.THRESHOLD)

    @classmethod
    def cc_number(cls, series):
        return cls.pattern_match(
            cls.sample(series), "|".join(Patterns.CCNUMBER), cls.THRESHOLD)

    @classmethod
    def city(cls, series):
        return cls.lookup_match(cls.sample(series), CITY_DATA, cls.THRESHOLD)

    @classmethod
    def country(cls, series):
        return cls.lookup_match(cls.sample(series),
                                COUNTRY_DATA, cls.THRESHOLD)

    @classmethod
    def datetime(cls, series):
        sample = cls.sample(series)
        row_count = len(sample)
        true_values = 0
        for val in sample:
            try:
                parse(val)
                true_values += 1
            except:
                pass
        if true_values >= (row_count * cls.THRESHOLD):
            return True
        else:
            return False

    @classmethod
    def email(cls, series):
        return cls.pattern_match(
            cls.sample(series), "|".join(Patterns.EMAIL), cls.THRESHOLD)

    @classmethod
    def enum(cls, series):
        try:
            l = list(series.dropna().apply(lambda x: int(x)))
        except:
            return False
        return l == list(range(min(l), max(l) + 1))

    @classmethod
    def first_name(cls, series):
        return cls.lookup_match(
            cls.sample(series), FIRSTNAME_DATA, cls.THRESHOLD)

    @classmethod
    def full_address(cls, series):
        return False

    @classmethod
    def gender(cls, series):
        return cls.pattern_match(
            cls.sample(series), "|".join(Patterns.GENDER), cls.THRESHOLD)

    @classmethod
    def integer(cls, series):
        return cls.pattern_match(
            cls.sample(series), "|".join(Patterns.INTEGER), cls.THRESHOLD)

    @classmethod
    def ip_address(cls, series):
        return cls.pattern_match(
            cls.sample(series), "|".join(Patterns.IPADDRESS), cls.THRESHOLD)

    @classmethod
    def last_name(cls, series):
        return cls.lookup_match(cls.sample(series), LASTNAME_DATA,
                                cls.THRESHOLD)

    @classmethod
    def number(cls, series):
        return cls.pattern_match(
            cls.sample(series), "|".join(Patterns.NUMBER), cls.THRESHOLD)

    @classmethod
    def phone_number(cls, series):
        return cls.pattern_match(
            cls.sample(series), "|".join(Patterns.PHONENUMBER), cls.THRESHOLD)

    @classmethod
    def ss_number(cls, series):
        return cls.pattern_match(
            cls.sample(series), "|".join(Patterns.SSNUMBER), cls.THRESHOLD)

    @classmethod
    def state(cls, series):
        return cls.lookup_match(cls.sample(series), STATE_DATA, cls.THRESHOLD)

    @classmethod
    def street_address(cls, series):
        return cls.pattern_match(
            cls.sample(series), "|".join(Patterns.STREETADDRESS),
            cls.THRESHOLD)

    @classmethod
    def zip(cls, series):
        return cls.pattern_match(
            cls.sample(series), "|".join(Patterns.ZIP), cls.THRESHOLD)