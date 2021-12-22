import datetime
import re

from uuid import uuid4
import pandas as pd

from .suggest import Suggestion
from .validate import Validation
from ..exceptions import PayloadError, InvalidDataTypeError, DuplicateNameError
from ..days.custom_types import *


class DaysDataFrame:
    def __init__(self, df, payload=None):
        if not payload:
            payload = dict()
        self._columns = [DaysSeries(x, i, True) for i, (_, x) in
                         enumerate(df.items())]
        self.uid = payload.get('uid', "Undefined")
        if payload.get('sheet_index'):
            sheet_index = payload.get('sheet_index', None)
            self.uid = f"{self.uid}#{sheet_index}" if sheet_index else self.uid
        self.name = payload.get('FileName', "Undefined")
        self.table_name = payload.get('TableName', "Undefined")
        self.size = payload.get('SizeInKb', 0)
        self.action_sequence = list()

    @property
    def columns(self):
        cols = list()
        for x in self._columns:
            if x.visible:
                cols.append(x)
        return sorted(cols, key=lambda value: value.index)

    @property
    def all_columns(self):
        cols = [x for x in self._columns]
        return sorted(cols, key=lambda x: x.index)

    @property
    def display_name(self):
        header = [col.display_name for col in self.columns]
        while True:
            try:
                header.remove(None)
            except ValueError:
                break

        return header

    @property
    def data_frame(self):
        data = [x.series for x in self.columns]
        if len(data) == 0:
            return pd.DataFrame()
        return pd.concat(data, axis=1, keys=self.display_name)

    @property
    def row_count(self):
        return len(self.data_frame)

    @property
    def column_count(self):
        return len(self.columns)

    @property
    def columns_schema(self):
        return [x.column_schema for x in self.all_columns]

    @property
    def schema(self):
        return {
            "FileName": self.name,
            "TableName": self.table_name,
            "ColumnCount": self.column_count,
            "RowCount": self.row_count,
            "SizeInKb": self.size,
            "ActionSequence": self.action_sequence,
            "Columns": self.columns_schema
        }

    def __len__(self):
        return len(self.data_frame)

    def __str__(self):
        return str(self.schema)

    def __getitem__(self, key):
        for ser in self.all_columns:
            if ser.id == key or ser.index == key:
                return ser
        raise ValueError(f"Id or index {key} does not exist.")

    def to_json(self, row_count=None, start=0, value_only=True):
        data = dict([(x.to_json(row_count, start, value_only=value_only))
                     for x in self.all_columns])
        return data

    def to_excel(self, destination=None):
        pass

    def to_csv(self, destination=None, show_index=False):
        file_path = f"{destination}{self.uid}.csv"
        df = self.data_frame.replace(['<NA>'], '')
        df.to_csv(path_or_buf=file_path,
                  header=self.display_name, index=show_index)
        return file_path

    def change_name(self, _id, new_name):
        if new_name in [x.display_name for x in self.columns]:
            raise ValueError("Cannot have more than one column with the same "
                             "name.")
        self[_id].display_name = new_name

    def new_column(self, series, index=None):
        if not index:
            index = max([x.index for x in self._columns]) + 1
        ds = DaysSeries(series, index)

        for i, col in enumerate(self._columns):
            if col.index >= index:
                self._columns[i].index += 1

        self._columns.insert(index, ds)
        return index

    def update_action_sequence(self, action=None):
        if not action:
            self.action_sequence.pop()
            return
        self.action_sequence.append(action)

    def remove_column(self, _id):
        index = self[_id].index
        for i, col in enumerate(self._columns):
            if col.index > index:
                self._columns[i].index -= 1
        self._columns.pop(index)

    def new_column_name(self, name, limit=10):
        column_names = set(x.name.lower() for x in self.columns)
        column_names.update(set(x.display_name.lower() for x in self.columns))
        new_name = name
        for i in range(1, limit):
            _ = new_name.lower()
            if _ in column_names:
                new_name = f"{name}__{i}"
            else:
                break
        else:
            raise DuplicateNameError(name)

        return new_name


class DaysSeries:
    def __init__(self, series, index, original=False):
        self.id = str(uuid4())
        self.index = index
        self.series = series
        self.original = original

        self.custom_type = "STRING"
        self.data_type = "string"
        self.display_name = self.series.name
        self.distinct_count = self.series.nunique()
        self.extended = dict()
        self.name = self.series.name
        self.non_null_count = len(self.series.notnull())
        self.visible = True
        self.suggest_type()
        self.series_date_format()
        self.valid_count = -1

    @property
    def row_count(self):
        return len(self.series)

    @property
    def column_schema(self):
        return {
            "customType": self.custom_type,
            "dataType": self.data_type,
            "displayName": self.display_name,
            "distinctCount": self.distinct_count,
            "extended": self.extended,
            "id": self.id,
            "index": self.index,
            "name": self.name,
            "nonNullCount": self.non_null_count,
            "validCount": self.valid_count,
            "visible": self.visible
        }

    def __str__(self):
        return f"DAYS Series - {self.display_name} ({self.index})"

    def __repr__(self):
        return f"DaysSeries(---, index={self.index}, name={self.display_name})"

    def __len__(self):
        return len(self.series)

    def __getitem__(self, key: int):
        return self.series[key]

    def apply(self, func, invalid="INVALID"):
        self.series = self.series.apply(func(invalid=invalid))

    def to_json(self, row_count=None, start=0, value_only=True):
        if not row_count:
            end_index = self.row_count
        else:
            end_index = start + row_count
        if value_only:
            values = dict([(i, str(val)) for i, val in
                           enumerate(list(self.series)[start:end_index])])
        else:
            values = dict(
                [(i, {"value": str(val), "validMeta": val.VALIDATION_META})
                 for i, val in enumerate(list(self.series)[start:end_index])])
        return self.display_name, values

    def change_display_name(self, new_name):
        self.display_name = new_name

    def suggest_type(self):
        self.series, self.custom_type = Suggestion.suggest_type(self.series)

    def validate(self, custom_type=None, legacy=True):
        if not custom_type:
            custom_type = self.custom_type
        if legacy:
            return Validation.validate(self.series, custom_type)
        self.series = Validation.validate(self.series, custom_type)
        self.valid_count = len(self.series.loc[lambda x: x != 'INVALID'])

    def substitute(self, match_str, replace_str):
        if match_str:
            self.series = pd.Series(
                [x.replace(match_str, replace_str) for x in self.series])
        else:
            self.series = pd.Series(
                [x if x else replace_str for x in self.series])

    def date_format(self, date_format):
        date_list = []
        _format = self.extended.get("dateFormat", "%d-%m-%Y")
        for x in self.series:
            try:
                x = re.split(" |,|;|-|/|'|at|on|and|of|st|nd|rd|th", x)
                x = '-'.join([_ for _ in x if _])
                x = datetime.datetime.strptime(x, _format).strftime(date_format)
            except:
                x = ''
            date_list.append(Datetime(x))
        self.series = pd.Series(date_list)

    def format(self, casing):
        if casing == "lowerCase":
            self.series = self.series.str.lower()
        elif casing == "upperCase":
            self.series = self.series.str.upper()
        elif casing == "camelCase":
            self.series = self.series.str.title()
        else:
            raise PayloadError("casing", casing)

    def update_visibility(self, visible=False):
        self.visible = visible

    def update_value(self, row_index, new_value):
        old_value = self.series[row_index]
        self.series[row_index] = new_value
        return old_value

    def update_custom_type(self, new_custom_type):
        if new_custom_type in ['DATETIME', 'INTEGER', 'ENUM', 'NUMBER',
                               'STRING', 'EMAIL', 'ADDRESS', 'CITY', 'ZIP',
                               'COUNTRY', 'CCNUMBER', 'SSNUMBER', 'BOOLEAN',
                               'TIME', 'GENDER', 'PHONENUMBER', 'STATE',
                               'FIRSTNAME', 'LASTNAME']:
            self.custom_type = new_custom_type
        else:
            raise InvalidDataTypeError(self.display_name, new_custom_type)

    def insert_string(self, insert_str, insert_index):
        self.series = pd.Series(
            [self.insert_string_value(value, insert_str, insert_index)
             for value in self.series])

    @classmethod
    def insert_string_value(cls, value, insert_str, insert_index):
        if insert_index == 0:
            return insert_str + value
        elif insert_index == -1:
            return value + insert_str
        else:
            return value[:insert_index] + insert_str + value[insert_index:]

    def split_by_index(self, limit_index, split_indexes):
        series = []
        start = [0] + [x + 1 for x in split_indexes]
        end = split_indexes + [None]
        for x in self.series:
            x = x[start[limit_index]:end[limit_index]]
            series.append(String(x))
        self.series = pd.Series(series)

    def split_by_string(self, split_index, split_string, is_last=False):
        series = []
        if is_last:
            for x in self.series:
                x = f'{split_string}'.join(x.split(split_string)[split_index:])
                series.append(String(x))
        else:
            for x in self.series:
                x = self.get_index(x.split(split_string), split_index)
                series.append(String(x))
        self.series = pd.Series(series)

    @classmethod
    def get_index(cls, lst, index, default=''):
        return lst[index] if len(lst) > index else default

    def series_date_format(self):

        def find_format(input_value):
            if input_value:
                _value = re.split(" |,|;|-|/|'|at|on|and|of|st|nd|rd|th",
                                  input_value)
                _value = '-'.join([_ for _ in _value if _])
                for _format in date_formats.keys():
                    try:
                        datetime.datetime.strptime(_value, _format)
                        return _format
                    except:
                        pass
            return None

        if self.custom_type == 'DATE':
            date_formats = {
                '%d-%m-%Y': 0, '%m-%d-%Y': 0, '%Y-%d-%m': 0, '%Y-%m-%d': 0,
                '%d-%m': 0, '%m-%d': 0, '%Y-%m': 0, '%m-%Y': 0, '%d-%b-%Y': 0,
                '%b-%d-%Y': 0, '%Y-%d-%b': 0, '%Y-%b-%d': 0, '%d-%b': 0,
                '%b-%d': 0, '%Y-%b': 0, '%b-%Y': 0, '%d-%B-%Y': 0,
                '%B-%d-%Y': 0, '%Y-%d-%B': 0, '%Y-%B-%d': 0, '%d-%B': 0,
                '%Y-%B': 0, '%B-%Y': 0, '%d-%m-%y': 0, '%m-%d-%y': 0,
                '%y-%d-%m': 0, '%y-%m-%d': 0, '%y-%m': 0, '%m-%y': 0,
                '%d-%b-%y': 0, '%b-%d-%y': 0, '%y-%d-%b': 0, '%y-%b-%d': 0,
                '%y-%b': 0, '%b-%y': 0, '%d-%B-%y': 0, '%B-%d-%y': 0,
                '%y-%d-%B': 0, '%y-%B-%d': 0, '%y-%B': 0, '%B-%y': 0,
            }

            for value in self.series:
                _ = find_format(value)
                if _ in date_formats.keys():
                    date_formats[_] += 1

            date_formats = dict(
                sorted(date_formats.items(), key=lambda item: item[1],
                       reverse=True))

            self.extended['dateFormat'] = list(date_formats.keys())[0]
        elif self.custom_type == 'DATETIME':
            date_formats = {
                '%d-%m-%Y-%H:%M:%S': 0, '%m-%d-%Y-%H:%M:%S': 0,
                '%Y-%d-%m-%H:%M:%S': 0, '%Y-%m-%d-%H:%M:%S': 0,
                '%d-%m-%H:%M:%S': 0, '%m-%d-%H:%M:%S': 0,
                '%Y-%m-%H:%M:%S': 0, '%m-%Y-%H:%M:%S': 0,
                '%d-%b-%Y-%H:%M:%S': 0, '%b-%d-%Y-%H:%M:%S': 0,
                '%Y-%d-%b-%H:%M:%S': 0, '%Y-%b-%d-%H:%M:%S': 0,
                '%d-%b-%H:%M:%S': 0, '%b-%d-%H:%M:%S': 0, '%Y-%b-%H:%M:%S': 0,
                '%b-%Y-%H:%M:%S': 0, '%d-%B-%Y-%H:%M:%S': 0,
                '%B-%d-%Y-%H:%M:%S': 0, '%Y-%d-%B-%H:%M:%S': 0,
                '%Y-%B-%d-%H:%M:%S': 0, '%d-%B-%H:%M:%S': 0,
                '%Y-%B-%H:%M:%S': 0, '%B-%Y-%H:%M:%S': 0,
                '%d-%m-%y-%H:%M:%S': 0, '%m-%d-%y-%H:%M:%S': 0,
                '%y-%d-%m-%H:%M:%S': 0, '%y-%m-%d-%H:%M:%S': 0,
                '%y-%m-%H:%M:%S': 0, '%m-%y-%H:%M:%S': 0,
                '%d-%b-%y-%H:%M:%S': 0, '%b-%d-%y-%H:%M:%S': 0,
                '%y-%d-%b-%H:%M:%S': 0, '%y-%b-%d-%H:%M:%S': 0,
                '%y-%b-%H:%M:%S': 0, '%b-%y-%H:%M:%S': 0,
                '%d-%B-%y-%H:%M:%S': 0, '%B-%d-%y-%H:%M:%S': 0,
                '%y-%d-%B-%H:%M:%S': 0, '%y-%B-%d-%H:%M:%S': 0,
                '%y-%B-%H:%M:%S': 0, '%B-%y-%H:%M:%S': 0, '%d-%m-%Y-%H:%M': 0,
                '%m-%d-%Y-%H:%M': 0, '%Y-%d-%m-%H:%M': 0, '%Y-%m-%d-%H:%M': 0,
                '%d-%m-%H:%M': 0, '%m-%d-%H:%M': 0, '%Y-%m-%H:%M': 0,
                '%m-%Y-%H:%M': 0, '%d-%b-%Y-%H:%M': 0, '%b-%d-%Y-%H:%M': 0,
                '%Y-%d-%b-%H:%M': 0, '%Y-%b-%d-%H:%M': 0, '%d-%b-%H:%M': 0,
                '%b-%d-%H:%M': 0, '%Y-%b-%H:%M': 0, '%b-%Y-%H:%M': 0,
                '%d-%B-%Y-%H:%M': 0, '%B-%d-%Y-%H:%M': 0, '%Y-%d-%B-%H:%M': 0,
                '%Y-%B-%d-%H:%M': 0, '%d-%B-%H:%M': 0, '%Y-%B-%H:%M': 0,
                '%B-%Y-%H:%M': 0, '%d-%m-%y-%H:%M': 0, '%m-%d-%y-%H:%M': 0,
                '%y-%d-%m-%H:%M': 0, '%y-%m-%d-%H:%M': 0, '%y-%m-%H:%M': 0,
                '%m-%y-%H:%M': 0, '%d-%b-%y-%H:%M': 0, '%b-%d-%y-%H:%M': 0,
                '%y-%d-%b-%H:%M': 0, '%y-%b-%d-%H:%M': 0, '%y-%b-%H:%M': 0,
                '%b-%y-%H:%M': 0, '%d-%B-%y-%H:%M': 0, '%B-%d-%y-%H:%M': 0,
                '%y-%d-%B-%H:%M': 0, '%y-%B-%d-%H:%M': 0, '%y-%B-%H:%M': 0,
                '%B-%y-%H:%M': 0,
            }

            for value in self.series:
                _ = find_format(value)
                if _ in date_formats.keys():
                    date_formats[_] += 1

            date_formats = dict(
                sorted(date_formats.items(), key=lambda item: item[1],
                       reverse=True))

            self.extended['dateFormat'] = list(date_formats.keys())[0]
