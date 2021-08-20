from copy import deepcopy

import pandas as pd
from .validator import Validator
from app.exceptions import PayloadError, InvalidDataTypeError
from app.config.validation_meta import VALIDATION_CONFIG


class ColumnHandler:
    @classmethod
    def execute(cls, df, schema, payload):
        action = payload['action']
        params = payload.get('inputParams', [{}])
        new_schema = list()
        action_sequence = {'action': action}
        _df = pd.DataFrame()
        insert_indexes = []
        if action in ["upperCase", "lowerCase", "camelCase"]:
            try:
                indexes = params[0]['indexes']
            except:
                raise PayloadError("indexes", "None")
            try:
                keep_original = params[0]['keepOriginal']
            except:
                keep_original = None
            _df, new_schema, insert_indexes = cls._casing(
                casing=action,
                df=df,
                indexes=indexes,
                keep_original=keep_original,
                schema=schema)
            if keep_original is not None:
                action_sequence.update({
                    'indexes': indexes,
                    'keeOriginal': keep_original
                })
            else:
                action_sequence.update({'indexes': indexes})
        elif action == "changeType":
            try:
                indexes = params[0]['indexes']
            except:
                raise PayloadError("indexes", "None")
            try:
                new_types = params[0]['newType']
            except:
                raise PayloadError("newType", "None")
            _df, new_schema = cls._change_type(
                df=df,
                indexes=indexes,
                new_types=new_types,
                schema=schema)
            action_sequence.update({
                'indexes': indexes,
                'type': new_types,
                'schema': deepcopy([schema['Columns'][index]
                                    for index in indexes])
            })
        elif action == "concatenate":
            try:
                indexes = params[0]['indexes']
            except:
                raise PayloadError("indexes", "None")
            try:
                join_char = params[0]['joinChar']
            except:
                raise PayloadError("joinChar", "None")
            try:
                keep_original = params[0]['keepOriginal']
            except:
                keep_original = None
            _df, new_schema, insert_indexes = cls._concat(
                df=df,
                indexes=indexes,
                join_char=join_char,
                keep_original=keep_original,
                schema=schema)
            if keep_original is not None:
                action_sequence.update({
                    'indexes': indexes,
                    'joinCharacter': join_char,
                    'keeOriginal': keep_original
                })
            else:
                action_sequence.update({
                    'indexes': indexes,
                    'joinCharacter': join_char
                })
        elif action == "remove":
            try:
                indexes = params[0]['indexes']
            except:
                raise PayloadError("indexes", "None")
            _df, new_schema = cls._remove(
                df=df,
                indexes=indexes)
            action_sequence.update({
                'indexes': indexes
            })
        elif action == "formatDateTime":
            try:
                indexes = params[0]['indexes']
            except:
                raise PayloadError("indexes", "None")
            try:
                new_datetime_format = params[0]['datetimeFormat']
            except:
                raise PayloadError("datetimeFormat", "None")
            _df, new_schema = cls._change_date_format(
                df=df,
                indexes=indexes,
                new_datetime_format=new_datetime_format,
                schema=schema)
            action_sequence.update({
                'indexes': indexes,
                'datetimeFormat': new_datetime_format,
                'schema': deepcopy([schema['Columns'][index]
                                    for index in indexes])
            })
        elif action == "rename":
            try:
                indexes = params[0]['indexes']
            except:
                raise PayloadError("indexes", "None")
            try:
                display_names = params[0]['displayNames']
            except:
                raise PayloadError("displayNames", "None")
            cols = [c['displayName'] for c in schema['Columns']]
            if len(display_names) != len(set(display_names)):
                raise PayloadError("displayNames", display_names,
                                   "Cannot have duplicate names.")
            for d_name in display_names:
                if d_name in cols:
                    raise PayloadError("displayNames", display_names,
                                       "Cannot have duplicate names.")
            _df, new_schema = cls._rename(
                df=df,
                indexes=indexes,
                display_names=display_names)
            action_sequence.update({
                'indexes': indexes,
                'displayNames': display_names,
                'schema': deepcopy([schema['Columns'][index]
                                    for index in indexes])
            })
        elif action == "substitute":
            try:
                indexes = params[0]['indexes']
            except:
                raise PayloadError("indexes", "None")
            try:
                match_str = params[0]['matchStr']
            except:
                raise PayloadError("matchStr", "None")
            try:
                replace_str = params[0]['replaceStr']
            except:
                raise PayloadError("replaceStr", "None")
            try:
                keep_original = params[0]['keepOriginal']
            except:
                keep_original = None
            _df, new_schema, insert_indexes = cls._sub(
                df=df,
                indexes=indexes,
                match_str=match_str,
                replace_str=replace_str,
                keep_original=keep_original,
                schema=schema)
            if keep_original is not None:
                action_sequence.update({
                    'indexes': indexes,
                    'matchStr': match_str,
                    'replaceStr': replace_str,
                    'keeOriginal': keep_original
                })
            else:
                action_sequence.update({
                    'indexes': indexes,
                    'matchStr': match_str,
                    'replaceStr': replace_str
                })
        elif action == "validate":
            try:
                indexes = params[0]['indexes']
            except:
                raise PayloadError("indexes", "None")
            try:
                valid_types = params[0]['validType']
                if isinstance(valid_types, str):
                    valid_types = [valid_types]
            except:
                raise PayloadError("validType", "None")

            _payload = list(zip(indexes, valid_types))
            _payload = sorted(_payload, key=lambda x: x[0])
            i = 0
            insert_indexes = list()
            for index, valid_type in _payload:
                insert_index = index + i + 1
                column_name = df.columns[index + i]
                display_name = column_name
                for col in schema['Columns']:
                    if index == col['index']:
                        display_name = col['displayName']

                try:
                    validation_info = VALIDATION_CONFIG[valid_type]
                except:
                    raise PayloadError("validType", valid_type)

                extended_function = validation_info.get('extended_function')
                if extended_function:
                    _df, _insert_index = extended_function(
                        df=df,
                        index=index + i,
                        column_name=column_name,
                        display_name=display_name,
                        t_f=params[0].get('t/f', False),
                        validation=validation_info)
                else:
                    _df, _insert_index = Validator.std_regex(
                        df=df,
                        index=index + i,
                        display_name=display_name,
                        column_name=column_name,
                        valid_type=valid_type,
                        t_f=params[0].get('t/f', False),
                        validation=validation_info)
                df = _df
                insert_indexes.append(insert_index)
                i += 1
            action_sequence.update({
                'indexes': indexes,
                'validTypes': valid_types
            })
        elif action == "validate-complex":
            try:
                valid_type = params[0]['validType'][0]
            except:
                raise PayloadError("validType", "None")
            if valid_type == "ADDRESS":
                _df, insert_indexes = Validator.address(
                    address1_index=params[0].get('address1_index'),
                    address2_index=params[0].get('address2_index'),
                    city_index=params[0].get('city_index'),
                    df=df,
                    schema=schema,
                    state_index=params[0].get('state_index'),
                    t_f=params[0].get('t/f', False),
                    zipcode_index=params[0].get('zipcode_index'))
            else:
                raise PayloadError("validType", valid_type)
            action_sequence.update({
                'validTypes': valid_type
            })
        else:
            raise PayloadError("action", action)
        return _df, new_schema, action_sequence, insert_indexes

    @staticmethod
    def _casing(df, casing, indexes, schema, keep_original):
        indexes.sort()
        insert_indexes = []
        new_schema = list()
        i = 0
        for _index in indexes:
            column_name = df.columns[_index + i]
            display_name = column_name
            for col in schema['Columns']:
                if _index == col['index']:
                    display_name = col['displayName']
                    break
            if keep_original is not None:
                sub_schema = {
                    "index": _index + i,
                    "visible": keep_original
                }
                new_schema.append(sub_schema)
            series = df[column_name]
            series = series.astype(object).where(series.notnull(), "")
            series = series.astype('string')
            new_name = f"{casing}_{display_name}"
            if casing == "lowerCase":
                new_series = series.str.lower()
            elif casing == "upperCase":
                new_series = series.str.upper()
            elif casing == "camelCase":
                new_series = series.str.title()
            else:
                raise PayloadError("casing", casing)
            ii = _index + i + 1
            insert_indexes.append(ii)
            i += 1
            dupe_limit = 5
            while True:
                if dupe_limit == 0:
                    raise Exception("too many dupe column names")
                try:
                    df.insert(ii, new_name, new_series)
                except ValueError:
                    dupe_limit -= 1
                    _ = new_name.split('__')
                    if len(_) == 1 or not _[-1].isnumeric():
                        new_name = new_name + "__1"
                    else:
                        new_name = '__'.join(_[:-1]) + f"__{int(_[-1]) + 1}"
                    continue
                break
        return df, new_schema, insert_indexes

    @staticmethod
    def _concat(df, indexes, schema, keep_original, join_char=" "):
        if len(indexes) < 2:
            raise PayloadError("indexes", indexes,
                               f"Need at least 2 columns to concatenate.")
        new_series = pd.Series(["" for _ in range(len(df))])
        insert_indexes = [max(indexes) + 1]
        new_schema = list()
        first = True
        i = 0
        names = list()
        for _index in indexes:
            column_name = df.columns[_index]
            display_name = column_name
            for col in schema['Columns']:
                if _index == col['index']:
                    display_name = col['displayName']
                    break
            if keep_original is not None:
                sub_schema = {
                    "index": _index,
                    "visible": keep_original
                }
                new_schema.append(sub_schema)
            names.append(display_name)
            series = df[column_name]
            series = series.astype(object).where(series.notnull(), "")
            series = series.astype('string')
            if first:
                join_by = ""
            else:
                join_by = join_char
            new_series = new_series.str.cat(series, sep=join_by, na_rep='')
            first = False
            i += 1
        new_name = f"concat_{'_'.join(names)}"
        dupe_limit = 5
        while True:
            if dupe_limit == 0:
                raise Exception("too many dupe column names")
            try:
                df.insert(insert_indexes[0], new_name, new_series)
            except ValueError:
                dupe_limit -= 1
                _ = new_name.split('__')
                if len(_) == 1 or not _[-1].isnumeric():
                    new_name = new_name + "__1"
                else:
                    new_name = '__'.join(_[:-1]) + f"__{int(_[-1]) + 1}"
                continue
            break
        return df, new_schema, insert_indexes

    @staticmethod
    def _sub(df, indexes, match_str, replace_str, schema, keep_original):
        indexes.sort()
        new_schema = list()
        insert_indexes = []
        i = 0
        for _index in indexes:
            column_name = df.columns[_index + i]
            for col in schema['Columns']:
                if _index == col['index']:
                    break
            if keep_original is not None:
                sub_schema = {
                    "index": _index + i,
                    "visible": keep_original
                }
                new_schema.append(sub_schema)
            series = df[column_name]
            series = series.astype(object).where(series.notnull(), "")
            series = series.astype('string')
            new_series = series.str.replace(match_str, replace_str)
            new_name = f"sub_{column_name}"
            ii = _index + i + 1
            insert_indexes.append(ii)
            i += 1
            dupe_limit = 5
            while True:
                if dupe_limit == 0:
                    raise Exception("too many dupe column names")
                try:
                    df.insert(ii, new_name, new_series)
                except ValueError:
                    dupe_limit -= 1
                    _ = new_name.split('__')
                    if len(_) == 1 or not _[-1].isnumeric():
                        new_name = new_name + "__1"
                    else:
                        new_name = '__'.join(_[:-1]) + f"__{int(_[-1]) + 1}"
                    continue
                break
        return df, new_schema, insert_indexes

    @staticmethod
    def _change_type(df, new_types, indexes, schema, date_format=None):
        if isinstance(new_types, str):
            new_types = [new_types for _ in range(len(indexes))]
        _payload = list(zip(indexes, new_types))
        _payload = sorted(_payload, key=lambda x: x[0])
        new_schema = list()
        for _index, _new_type in _payload:
            column_name = df.columns[_index]
            schema = {
                "index": _index,
                "customType": _new_type
            }
            new_schema.append(schema)
            if _new_type == 'DATETIME':
                try:
                    df[column_name] = pd.to_datetime(df[column_name].astype(str))
                except Exception as e:
                    raise InvalidDataTypeError(column_name, "DATETIME")
                    # raise Exception(f"dtype {_new_type} is not recognized.")
            elif _new_type in ['INTEGER', 'ENUM']:
                try:
                    df[column_name] = df[column_name].astype("float")
                    df[column_name] = df[column_name].astype("Int64")
                except Exception as e:
                    raise InvalidDataTypeError(column_name, "INTEGER")
            elif _new_type in ['NUMBER']:
                try:
                    df[column_name] = df[column_name].astype("float")
                except Exception as e:
                    raise InvalidDataTypeError(column_name, "NUMBER")
            elif _new_type in ['STRING', 'EMAIL', 'ADDRESS', 'CITY', 'ZIP',
                               'COUNTRY', 'CCNUMBER', 'SSNUMBER', 'BOOLEAN',
                               'TIME', 'GENDER', 'PHONENUMBER', 'STATE',
                               'FIRSTNAME', 'LASTNAME']:
                df[column_name] = df[column_name].astype("string")
            else:
                raise Exception(f"dtype {_new_type} is not recognized.")
        return df, new_schema

    @staticmethod
    def _remove(df, indexes):
        """TODO: update pandas dtype associated with custom type
        """
        indexes.sort()
        new_schema = list()
        for _index in indexes:
            schema = {
                "index": _index,
                "visible": False
            }
            new_schema.append(schema)
        return df, new_schema

    @staticmethod
    def _change_date_format(df, indexes, new_datetime_format, schema):
        '''TODO: update pandas dtype associated with datetime format
        '''
        indexes.sort()
        new_schema = list()
        for _index in indexes:
            sub_schema = {
                "index": _index,
                "datetimeFormat": new_datetime_format,
                "customType": "DATETIME"
            }
            new_schema.append(sub_schema)
            column_schema = schema['Columns'][_index]
            column_name = column_schema['name']
            if column_schema['dataType'] != 'datetime64[ns]':
                try:
                    df[column_name] = pd.to_datetime(df[column_name])
                except Exception as e:
                    raise InvalidDataTypeError(column_name, "DATETIME")
        return df, new_schema

    @staticmethod
    def _rename(df, indexes, display_names):
        """TODO: update pandas dtype associated with custom type
        """
        _payload = list(zip(indexes, display_names))
        _payload = sorted(_payload, key=lambda x: x[0])
        new_schema = list()
        for _index, _display_name in _payload:
            schema = {
                "displayName": _display_name,
                "index": _index
            }
            new_schema.append(schema)
        return df, new_schema
