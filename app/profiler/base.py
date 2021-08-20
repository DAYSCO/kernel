import json
import numpy as np
import pandas as pd
from app.exceptions import PayloadError
from app.controllers.data_types import *


class Profiler:
    '''Base class containing rudimentary data frame profiling
    functions.
    '''

    @classmethod
    def get_head(cls, df, rows:int):
        '''Function takes in dataframe object and number of rows
        requested from the top and returns a json formatted string
        representing the data.
        :params df: (DataFrame) data frame object
                rows: (int) number of rows to be returned
        :return: json formatted string
        :rtype: str
        '''

        return cls.jsonify(df.head(rows))

    @classmethod
    def get_tail(cls, df, rows:int):
        '''Function takes in dataframe object and number of rows
        requested from the bottom and returns a json formatted string
        representing the data.
        :params df: (DataFrame) data frame object
                rows: (int) number of rows to be returned
        :return: json formatted string
        :rtype: str
        '''

        return cls.jsonify(df.tail(rows))

    @classmethod
    def get_data(cls, df, schema, start_index:int, row_count:int, sort_column_index=None, sort_ascending:bool=True):
        '''Function takes in dataframe object, start row index and number of rows
        and returns a json formatted string representing the data.
        :params df: (DataFrame) data frame object
                startIndex: (int) starting index for data
                rowCount: (int) number of rows to be returned
        :return: json formatted string
        :rtype: str
        '''
        end_index = start_index + row_count
        if start_index < 0 or start_index > len(df):
            raise PayloadError("startIndex", start_index, f"Index out of range, must be between (0 and {len(df)}).")
        if row_count < 1 or row_count > len(df) - start_index:
            raise PayloadError("rowCount", row_count, f"Index out of range, must be between (1 and {len(df) - start_index}).")
        if sort_column_index:
            for sci in sort_column_index:
                if sci < 0 or sci > len(df.columns) - 1:
                    raise PayloadError("sortColumnIndex", sci, f"Index out of range, must be between (0 and {len(df.columns) - 1}).")
            index_columns = [df.columns[i] for i in sort_column_index]
            return cls.jsonify(df.set_index(index_columns).sort_index(ascending=sort_ascending).reset_index().iloc[start_index:end_index, :])
        return cls.jsonify(df.iloc[start_index:end_index, :], schema)

    @classmethod
    def get_columns(cls, df):
        '''Function takes in dataframe object and returns list of
        column names in a json formatted string.
        :params df: (DataFrame) data frame object
        :return: json formatted string
        :rtype: str
        '''

        payload = {
            "columns": list(df.columns)
        }

        return cls.jsonify(payload)

    @classmethod
    def get_column_count(cls, df):
        '''Function takes in dataframe object and returns length of
        columns as an int.
        :params df: (DataFrame) data frame object
        :return: length of column count
        :rtype: int
        '''

        col = cls.get_columns(df)
        return len(col['columns'])

    @classmethod
    def get_row_count(cls, df):
        '''TODO
        :params df: (DataFrame) data frame object
        :return: json formatted string
        :rtype: str
        '''

        pass

    @classmethod
    def get_dimensions(cls, df):
        '''TODO
        :params df: (DataFrame) data frame object
        :return: json formatted string
        :rtype: str
        '''
        
        payload = {
            "column_count": df.shape[0],
            "row_count": df.shape[1]
        }
        
        return cls.jsonify(payload)

    @classmethod
    def get_column_info(cls, df):
        '''TODO
        :params df: (DataFrame) data frame object
        :return: json formatted string
        :rtype: str
        '''

        pass

    @classmethod
    def get_data_info(cls, df):
        '''TODO
        :params df: (DataFrame) data frame object
        :return: json formatted string
        :rtype: str
        '''

        pass

    @staticmethod
    def jsonify(obj, schema={}):
        '''Function takes in any data object and returns a json
        formatted string representing the data.
        :params obj: data object
        :return: json formatted string
        :rtype: str
        '''
        if isinstance(obj, pd.DataFrame):
            obj = obj.replace({np.nan: ""})
            _payload = obj.to_dict()
            cols = schema.get('Columns', list())
            payload = dict()
            for col in cols:
                if col['name'] in _payload.keys():
                    if col['dataType'] == 'object':
                        payload.update({col['displayName']: obj[col['name']].astype('string').to_dict()})
                    else:
                        payload.update({col['displayName']: _payload[col['name']]})
                if col['dataType'] == 'datetime64[ns]':
                    _payload[col['name']] = pd.to_datetime(obj[col['name']], errors='coerce')
                    payload[col['name']] = _payload[col['name']].dt.strftime(col['datetimeFormat']).to_dict()

            return json.dumps(payload)
        elif isinstance(obj, dict):
            return json.dumps(obj)
        else:
            raise Exception("Error: Object not recognized.")

