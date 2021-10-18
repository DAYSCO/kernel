from collections import Counter
from flask import jsonify
from pandas import Series
from dateutil.parser import parse

from app.exceptions import IDNotFoundError
from app.config.column_meta import SUGGESTION_CONFIG, TYPE_PATTERNS


class ActiveWorkingFiles:
    def __init__(self):
        self.working_files = list()

    def __getitem__(self, uid):
        for _ in self.working_files:
            if _.uid == uid or _.uid == f"{uid}#1":
                return _
        raise IDNotFoundError(uid)

    @property
    def keys(self):
        return [_.uid for _ in self.working_files]

    def add(self, wf):
        try:
            self.remove(wf.uid)
        except:
            pass
        self.working_files.append(wf)

    def remove(self, uid):
        self.working_files.remove(self[uid])

    def update_schema(self, uid, schema=None, action_sequence=None):
        if uid in self.keys:
            if schema:
                for incoming in schema:
                    self[uid].update_schema(incoming=incoming)
            if action_sequence:
                self[uid].update_action_sequence(
                    action_sequence=action_sequence)
        else:
            raise Exception(f"uid ({uid}) not recognized.")

    def update_df(self, uid, df):
        if uid in self.keys:
            self[uid].update_df(new_data_frame=df)
        else:
            raise Exception(f"uid ({uid}) not recognized.")


class WorkingFile:
    def __init__(self, uid, data_frame, file_name, file_size, sheet_index=None,
                 sheet_schema=None):
        self.uid = f"{uid}#{sheet_index}" if sheet_index else uid
        self.data_frame = data_frame
        self.name = file_name
        self.size = file_size
        self.sheet_schema = sheet_schema
        self.action_sequence = []
        self.column_names = list(data_frame.columns)
        self.columns = self.new_schema(self.column_names)
        self.update_types()

    @property
    def schema(self):
        return {
            "TableName": self.name,
            "ColumnCount": sum(
                [1 if x['visible'] is True else 0 for x in self.columns]),
            "RowCount": self.row_count,
            "SizeInKb": self.size,
            "ActionSequence": self.action_sequence,
            "Columns": self.columns
        }

    @property
    def row_count(self):
        return len(self.data_frame)

    def update_column_name(self):
        self.column_names = list(self.data_frame.columns)

    def column_details(self, column_name, column_index, ex={}):
        column = {
            "customType": ex.get('customType',
                                 "STRING") if ex else self.suggested_type(
                column_name),
            # "datetimeFormat": ex.get('datetimeFormat', "%Y-%m-%d"),
            "dataType": str(self.data_frame[column_name].dtype),
            "displayName": ex.get('displayName', column_name),
            "distinctCount": ex.get('distinctCount',
                                    self.distinct_count(column_name)),
            "extended": ex.get('extended', {}),
            "index": column_index,
            "name": column_name,
            "nonNullCount": ex.get(
                'nonNullCount', len(self.data_frame[column_name].notnull())),
            "visible": ex.get('visible', True)
        }
        return column

    def distinct_count(self, column_name):
        try:
            return len(self.data_frame[column_name].unique())
        except:
            return len(self.data_frame[column_name])

    @staticmethod
    def list_get(obj, index, default=None):
        try:
            return obj[index]
        except IndexError:
            return default

    def update_df(self, new_data_frame):
        new_columns = list(new_data_frame.columns)
        self.data_frame = new_data_frame
        self.columns = self.new_schema(new_columns, self.column_names)
        self.update_column_name()

    def new_schema(self, new_columns, old_columns=None):
        if not old_columns:
            old_columns = list()
        new_schema = list()
        for i, col in enumerate(new_columns):
            if col == self.list_get(old_columns, i):
                new_schema.append(self.columns[i])
            elif col not in old_columns:
                schema = self.column_details(column_name=col, column_index=i)
                new_schema.append(schema)
            else:
                if col in old_columns:
                    ex_i = old_columns.index(col)
                    old_schema = self.columns[ex_i]
                    old_schema['index'] = i
                    new_schema.append(old_schema)
        return new_schema

    def update_schema(self, incoming):
        column_index = incoming['index']
        column_name = self.columns[column_index]['name']
        column_schema = self.column_details(column_name=column_name,
                                            column_index=column_index,
                                            ex=self.columns[column_index])
        column_schema.update(incoming)
        self.columns[column_index].update(column_schema)

    def update_action_sequence(self, action_sequence=None):
        if action_sequence == 'undo':
            self.action_sequence.pop()
        else:
            self.action_sequence.append(action_sequence)

    @property
    def sample_count(self):
        row_count = len(self.data_frame)
        if row_count < 100:
            return row_count
        elif row_count < 10000:
            return row_count // 10
        else:
            return 1000

    def suggested_type(self, col):
        acceptable_percentage = 85
        row_count = self.sample_count
        data = self.data_frame[col].dropna()
        try:
            set(data)
        except TypeError:
            return "String"
        if row_count != len(self.data_frame[col]):
            data = data.sample(row_count, replace=True)
        for key in sorted(SUGGESTION_CONFIG):
            method = SUGGESTION_CONFIG[key]['method']
            if method == 'pattern':
                pattern = '|'.join(SUGGESTION_CONFIG[key]['value'])
                result = data.str.contains(pattern)
                true_values = result.value_counts().get(True, 0)
                if true_values >= (row_count * (acceptable_percentage / 100)):
                    return SUGGESTION_CONFIG[key]['type']
            elif method == 'lookup':
                result = set(data)
                true_values = 0
                result = result.intersection(SUGGESTION_CONFIG[key]['value'])
                count_values = Counter(data)
                for value in result:
                    true_values += count_values.get(value, 0)
                if true_values >= (row_count * (acceptable_percentage / 100)):
                    return SUGGESTION_CONFIG[key]['type']
            elif method == 'datetime':
                true_values = 0
                for value in data:
                    try:
                        parse(value)
                        true_values += 1
                    except:
                        pass
                if true_values >= (row_count * (acceptable_percentage / 100)):
                    return SUGGESTION_CONFIG[key]['type']
            else:
                return "STRING"
        return "STRING"

    def update_types(self):
        for i, col in enumerate(self.schema['Columns']):
            column_name = self.column_names[i]
            new_class = TYPE_PATTERNS.get(
                col['customType'], dict()).get('class')
            if new_class:
                series = self.data_frame[column_name]
                self.data_frame[column_name] = Series(
                    [new_class(_) for _ in list(series)])


class EmptyWF:
    def __init__(self, uid):
        self.uid = uid
        self.df = None
        self.name = None
        self.size = None
        self.schema = dict()

    @property
    def payload(self):
        return jsonify(self.schema)