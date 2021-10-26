import csv
import pandas as pd
from io import StringIO

from app.exceptions import FileParseError


class Ingester:
    """Class containing file handling methods.
    """

    @staticmethod
    def content_upload(contents, file_name):
        """Function takes in file content creates IO file to be
        converted to a DataFrame object and returned.
        :params content: (str) content from file
        :return: DataFrame object of csv
        :rtype: DataFrame
        """
        try:
            stream_io_file = StringIO(contents)
            df = pd.read_csv(stream_io_file, dtype='string')
            df.replace(['<NA>'], '', inplace=True)
            df.fillna('', inplace=True)
            return df
        except:
            raise FileParseError(file_name)

    @staticmethod
    def mpfile_upload(mp_file, file_name, sheet_name=None, file_type='csv'):
        """Function takes in open file converts to a DataFrame
        object and returned.
        :params mp_file: (FileStorage) open file
        :return: DataFrame object of csv
        :rtype: DataFrame
        """
        try:
            if file_type == 'xlsx' or file_type == 'xls':
                df = pd.read_excel(mp_file, sheet_name=sheet_name,
                                   dtype='string')
            elif file_type == 'json':
                df = pd.read_json(mp_file.stream, dtype='string')
            elif file_type == 'html':
                df = pd.read_html(mp_file.stream)[0]
                df = df.astype('string')
            else:
                try:
                    df = pd.read_csv(mp_file.stream, dtype='string')
                except Exception:
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(mp_file.read().decode()).delimiter
                    mp_file.stream.seek(0)
                    df = pd.read_csv(mp_file.stream, dtype='string',
                                     delimiter=delimiter)
            df.replace(['<NA>'], '', inplace=True)
            df.fillna('', inplace=True)
            return df
        except:
            raise FileParseError(file_name)

    @staticmethod
    def identify_file(file_name):
        """TODO: parse file name
        """
        return file_name.split('.')[-1].strip()

    @staticmethod
    def xml_table_parse(xml_contents):
        """TODO: parse xml tables
        """
        pass
