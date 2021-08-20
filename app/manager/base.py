import copy
import csv
import os
import pandas as pd
import sys
from io import StringIO


class Ingester:
    '''Class containing file handling methods.
    '''

    @staticmethod
    def content_upload(contents):
        '''Function takes in file content creates IO file to be
        converted to a DataFrame object and returned.
        :params content: (str) content from file
        :return: DataFrame object of csv
        :rtype: DataFrame
        '''
        stream_io_file = StringIO(contents)
        return pd.read_csv(stream_io_file, dtype=object)

    @staticmethod
    def mpfile_upload(mp_file, sheet_name=None, file_type='csv'):
        '''Function takes in open file converts to a DataFrame
        object and returned.
        :params mp_file: (FileStorage) open file
        :return: DataFrame object of csv
        :rtype: DataFrame
        '''
        if file_type == 'xlsx' or file_type == 'xls':
            return pd.read_excel(mp_file, sheet_name=sheet_name, dtype='string')
        else:
            try:
                return pd.read_csv(mp_file.stream, dtype='string')
            except Exception as e:
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(mp_file.read().decode()).delimiter
                mp_file.stream.seek(0)
                return pd.read_csv(mp_file.stream, dtype='string', delimiter=delimiter)


    @staticmethod
    def identify_file(file_name):
        '''TODO: parse file name 
        '''
        return file_name.split('.')[-1].strip()

    @staticmethod
    def xml_table_parse(xml_contents):
        '''TODO: parse xml tables
        '''
        pass


class Exporter:
    '''Class containing file handling methods.
    '''

    @staticmethod
    def to_csv(df, schema, show_index, uid):
        PLATFORM = sys.platform
        if PLATFORM in ['win32', 'cygwin', 'msys']:
            spl = "\\"
        elif PLATFORM in ['linux', 'linux2', 'darwin' , 'os2', 'os2emx']:
            spl = "/"
        else:
            raise Exception(f"ERROR: sys.platform unknown {PLATFORM}")
        base_dir = f"{os.getcwd()}{spl}exports"
        try:
            os.mkdir(base_dir)
        except FileExistsError:
            pass
        file_path = f"{base_dir}{spl}{uid}.csv"
        columns = [col['index'] if col['visible'] else None for col in schema.get('Columns', list())]
        header = [col['displayName'] if col['visible'] else None for col in schema.get('Columns', list())]
        while True:
            try:
                columns.remove(None)
            except ValueError:
                break
        while True:
            try:
                header.remove(None)
            except ValueError:
                break
        df = df.iloc[:, columns]
        df.to_csv(path_or_buf=file_path, header=header, index=show_index)
        return file_path
