import os
import re
import idna
import pandas as pd
from smartystreets_python_sdk import StaticCredentials, exceptions, Batch, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup as StreetLookup
from smartystreets_python_sdk.us_zipcode import Lookup as ZIPCodeLookup
from app.exceptions import PayloadError
from app.util import ConnectionManager


class Validator:
    SMARTYSTREETS_AUTH_TOKEN = os.environ.get('SMARTYSTREETS_AUTH_TOKEN', 'M5VB7vOR63EYUvkqQWzP')
    SMARTYSTREETS_AUTH_ID = os.environ.get('SMARTYSTREETS_AUTH_ID', '5aa199f9-3d5f-f2ba-b41f-74b953b5d1d6')
    USERID = "467DAYS06449"

    @classmethod
    def credit_card(cls, df, validation, index, display_name, column_name, invalid="INVALID", t_f=False):
        series = df[column_name]
        series = series.astype(object).where(series.notnull(), "")
        series = series.astype('string')
        if not t_f:
            new_series_v = [x if cls.luhn(str(x)) else '' for x in series]
            new_series = list()
            while True:
                try:
                    x = new_series_v.pop(0)
                    if x:
                        y = "Unknown Issuer"
                        names = validation['patterns']['subTypes']
                        patterns = validation['patterns']['patterns']
                        for name, pattern in zip(names, patterns):
                            pattern = re.compile(pattern)
                            if pattern.match(x):
                                y = name
                                break
                        new_series.append(y)
                    else:
                        new_series.append(invalid)
                except IndexError:
                    break
        else:
            new_series = ["TRUE" if cls.luhn(str(x)) else 'FALSE' for x in series]
        new_name = f"validation_{display_name}_creditCard"
        insert_index = index + 1
        dupe_limit = 5
        while True:
            if dupe_limit == 0:
                raise Exception("too many dupe column names")
            try:
                df.insert(insert_index, new_name, new_series)
            except ValueError:
                dupe_limit -= 1
                _ = new_name.split('__')
                if len(_) == 1 or not _[-1].isnumeric():
                    new_name = new_name + "__1"
                else:
                    new_name = '__'.join(_[:-1]) + f"__{int(_[-1]) + 1}"
                continue
            break
        return df, insert_index

    @classmethod
    def std_regex(cls, df, validation, display_name, column_name, index, valid_type, invalid="INVALID", t_f=False):
        pattern = re.compile('|'.join(validation['patterns']['patterns']))
        series = df[column_name]
        series = series.astype(object).where(series.notnull(), "")
        series = series.astype('string')
        if not t_f:
            new_series = [x if pattern.match(x) else invalid for x in series]
        else:
            new_series = ['TRUE' if pattern.match(x) else 'FALSE' for x in series]
        new_name = f"validation_{display_name}_{valid_type}"
        insert_index = index + 1
        dupe_limit = 5
        while True:
            if dupe_limit == 0:
                raise Exception("too many dupe column names")
            try:
                df.insert(insert_index, new_name, new_series)
            except ValueError:
                dupe_limit -= 1
                _ = new_name.split('__')
                if len(_) == 1 or not _[-1].isnumeric():
                    new_name = new_name + "__1"
                else:
                    new_name = '__'.join(_[:-1]) + f"__{int(_[-1]) + 1}"
                continue
            break
        return df, insert_index

    @classmethod
    def zip_code(cls, df, validation, index,  display_name, column_name, invalid="INVALID", t_f=False):
        new_series = pd.Series([], dtype="string")
        for x in cls.batch(df[column_name], 100):
            new_series = new_series.append(cls.smartystreet_zip_code(zipcode=list(x), invalid=invalid, t_f=t_f), ignore_index=True)
        new_name = f"validation_{display_name}_ZIPCODE"
        insert_index = index + 1
        dupe_limit = 5
        while True:
            if dupe_limit == 0:
                raise Exception("too many dupe column names")
            try:
                df.insert(insert_index, new_name, new_series)
            except ValueError:
                dupe_limit -= 1
                _ = new_name.split('__')
                if len(_) == 1 or not _[-1].isnumeric():
                    new_name = new_name + "__1"
                else:
                    new_name = '__'.join(_[:-1]) + f"__{int(_[-1]) + 1}"
                continue
            break
        return df, insert_index

    @classmethod
    def address(cls, df, validation, index,  display_name, column_name, invalid="no valid street address found", t_f=False):
        new_series = pd.Series([], dtype="string")
        for x in cls.batch(df[column_name], 100):
            new_series = new_series.append(cls.smartystreet(address_full=list(x), invalid=invalid, t_f=t_f), ignore_index=True)
        new_name = f"validation_{display_name}_ADDRESS"
        insert_index = index + 1
        dupe_limit = 5
        while True:
            if dupe_limit == 0:
                raise Exception("too many dupe column names")
            try:
                df.insert(insert_index, new_name, new_series)
            except ValueError:
                dupe_limit -= 1
                _ = new_name.split('__')
                if len(_) == 1 or not _[-1].isnumeric():
                    new_name = new_name + "__1"
                else:
                    new_name = '__'.join(_[:-1]) + f"__{int(_[-1]) + 1}"
                continue
            break
        return df, insert_index

    @classmethod
    def smartystreet(cls, address_full=[], addressee=[], street=[], street2=[], secondary=[], lastline=[], city=[], state=[], zipcode=[], invalid="INVALID", t_f=False):
        credentials = StaticCredentials(cls.SMARTYSTREETS_AUTH_ID, cls.SMARTYSTREETS_AUTH_TOKEN)
        client = ClientBuilder(credentials).build_us_street_api_client()
        batch = Batch()
        results = pd.Series([], dtype="string")
        if len(address_full) > 0:
            for x in address_full:
                batch.add(StreetLookup(x))
        else:
            max_v = max(len(addressee), len(street), len(street2), len(secondary), len(lastline), len(city), len(state), len(zipcode))
            addressee = cls.fill_list(addressee, max_v)
            street = cls.fill_list(street, max_v)
            street2 = cls.fill_list(street2, max_v)
            secondary = cls.fill_list(secondary, max_v)
            lastline = cls.fill_list(lastline, max_v)
            city = cls.fill_list(city, max_v)
            state = cls.fill_list(state, max_v)
            zipcode = cls.fill_list(zipcode, max_v)
            for i, (s, t, u, v, w, x, y, z) in enumerate(zip(addressee, street, street2, secondary, lastline, city, state, zipcode)):
                batch.add(StreetLookup())
                if s:
                    batch[i].addressee = s
                if t:
                    batch[i].street = t
                if u:
                    batch[i].street2 = u
                if v:
                    batch[i].secondary = v
                if w:
                    batch[i].lastline = w
                if x:
                    batch[i].city = x
                if y:
                    batch[i].state = y
                if z:
                    batch[i].zipcode = z
        try:
            client.send_batch(batch)
        except exceptions.SmartyException as err:
            print(err)
            raise err

        for i, lookup in enumerate(batch):
            candidates = lookup.result
            if len(candidates) == 0:
                if t_f:
                    r_ser = pd.Series(['FALSE'])
                else:
                    r_ser = pd.Series([invalid])
            else:
                if t_f:
                    r_ser = pd.Series(['TRUE'])
                else:
                    delivery_line_1 = candidates[0].delivery_line_1 or ''
                    delivery_line_2 = candidates[0].delivery_line_2 or ''
                    delivery_last_line = candidates[0].last_line or ''
                    address_details = f"{delivery_line_1} {delivery_line_2 + ' ' if delivery_line_2 else ''}{delivery_last_line}"
                    r_ser = pd.Series(address_details)
            results = results.append(r_ser, ignore_index=True)
        ConnectionManager(client.sender).close()
        return results

    @classmethod
    def smartystreet_zip_code(cls, zipcode=[], invalid="INVALID", t_f=False):
        credentials = StaticCredentials(cls.SMARTYSTREETS_AUTH_ID, cls.SMARTYSTREETS_AUTH_TOKEN)
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
                if t_f:
                    value = 'TRUE'
            except IndexError:
                value = invalid
                if t_f:
                    value = 'FALSE'
            r_ser = pd.Series([value])
            results = results.append(r_ser, ignore_index=True)
        ConnectionManager(client.sender).close()
        return results

    @staticmethod
    def luhn(cc_number):
        if cc_number.isnumeric():
            _ = list(cc_number)
            last = int(_.pop(-1))
            _ = _[::-1]
            _ = [x if i % 2 != 0 else str(int(x) * 2) for i, x in enumerate(_)]
            _ = [x if int(x) <= 9 else str(int(x) - 9) for x in _]
            s = sum([int(x) for x in _])
            return (s + last) % 10 == 0
        else:
            return False

    @staticmethod
    def batch(iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

    @staticmethod
    def fill_list(list_obj, max_v):
        if len(list_obj) == max_v:
            return list_obj
        else:
            return [None for _ in range(max_v)]

    @classmethod
    def validate_email(cls, df, validation, display_name, column_name, index, invalid="INVALID", t_f=False):
        pattern = re.compile('|'.join(validation['patterns']['patterns']))
        series = df[column_name]
        series = series.astype(object).where(series.notnull(), "")
        series = series.astype('string')
        if not t_f:
            new_series = [x if pattern.match(x) else invalid for x in series]
            domain_series = [x.split('@')[-1] for x in new_series]
            domain_validate_data = {x: Validator.email_domain_validation(x) for x in set(domain_series)}
            new_series = [value if domain_validate_data.get(domain) else invalid for value, domain in zip(new_series, domain_series)]
        else:
            new_series = ['TRUE' if pattern.match(x) else 'FALSE' for x in series]
        new_name = f"validation_{display_name}_email"
        insert_index = index + 1
        dupe_limit = 5
        while True:
            if dupe_limit == 0:
                raise Exception("too many dupe column names")
            try:
                df.insert(insert_index, new_name, new_series)
            except ValueError:
                dupe_limit -= 1
                _ = new_name.split('__')
                if len(_) == 1 or not _[-1].isnumeric():
                    new_name = new_name + "__1"
                else:
                    new_name = '__'.join(_[:-1]) + f"__{int(_[-1]) + 1}"
                continue
            break
        return df, insert_index

    @staticmethod
    def email_domain_validation(domain):

        if len(domain) == 0:
            return False

        try:
            domain = idna.uts46_remap(domain, std3_rules=False, transitional=False)
        except Exception as e:
            return False

        if domain.endswith("."):
            return False
        if domain.startswith("."):
            return False
        if ".." in domain:
            return False

        try:
            ascii_domain = idna.encode(domain, uts46=False).decode("ascii")
        except idna.IDNAError as e:
            return False

        try:
            domain_i18n = idna.decode(ascii_domain.encode('ascii'))
        except idna.IDNAError as e:
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