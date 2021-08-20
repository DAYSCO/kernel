import pandas as pd
from flask_api import status
from flask import jsonify
from app.manager import Ingester
from app.controllers import WorkingFile
from app.profiler import Profiler
from app.handler import ColumnHandler, TableHandler
from app.exceptions import IDNotFoundError, PayloadError, InvalidDataTypeError


class GenericCall:
    def __init__(self, request, working_files=None):
        self.headers = request.headers
        self.uid = self.headers.get('id')
        self.data = request.get_data().decode('utf-8')
        self.file_size = self.headers.get('size', 1234)
        self.file_name = self.headers.get('name', f'document_{self.uid}')
        self.json_response = request.get_json()
        self.payload = None
        self.method = request.method
        self.return_message = "successful request"
        self.return_code = status.HTTP_200_OK
        self.working_files = working_files


class UploadFile(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        self.mp_file = request.files.get('file')
        self.file_type = Ingester.identify_file(self.file_name)
        if not self.uid:
            self.return_message = "id missing from headers request"
            self.return_code = status.HTTP_400_BAD_REQUEST
        else:
            try:
                if self.file_type == 'txt' or self.file_type == 'csv':
                    self.working_files.add(
                        WorkingFile(
                            uid=self.uid,
                            data_frame=Ingester.mpfile_upload(self.mp_file,
                                                              self.file_type),
                            file_name=self.file_name,
                            file_size=self.file_size))
                elif self.file_type == 'xlsx' or self.file_type == 'xls':
                    sheet_names = pd.ExcelFile(self.mp_file).sheet_names
                    for index, sheet_name in enumerate(sheet_names):
                        self.working_files.add(
                            WorkingFile(uid=self.uid,
                                        data_frame=Ingester.mpfile_upload(
                                            mp_file=self.mp_file,
                                            file_type=self.file_type,
                                            sheet_name=sheet_name),
                                        file_name=self.file_name,
                                        file_size=self.file_size,
                                        sheet_index=index))
            except Exception as e:
                self.working_files = working_files
                self.return_message = repr(e)
                self.return_code = status.HTTP_400_BAD_REQUEST


class ReadFileContents(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        if not self.uid:
            self.return_message = "id missing from headers request"
            self.return_code = status.HTTP_400_BAD_REQUEST
        else:
            try:
                self.working_files.add(
                    WorkingFile(
                        uid=self.uid,
                        data_frame=Ingester.content_upload(self.data),
                        file_name=self.file_name,
                        file_size=self.file_size))
            except Exception as e:
                self.working_files = working_files
                self.return_message = repr(e)
                self.return_code = status.HTTP_400_BAD_REQUEST


class TableSchema(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        if not self.uid:
            self.return_message = "id missing from headers request"
            self.return_code = status.HTTP_400_BAD_REQUEST
        else:
            if self.method == "PUT":
                try:
                    new_schema = self.json_response.get('tableSchema', [])
                    self.working_files.update_schema(uid=self.uid,
                                                     schema=new_schema)
                except IDNotFoundError as e:
                    self.working_files = working_files
                    self.return_message = str(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                except Exception as e:
                    self.working_files = working_files
                    self.return_message = repr(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                    raise e
            elif self.method == "GET":
                try:
                    self.payload = jsonify(self.working_files[self.uid].schema)
                except IDNotFoundError as e:
                    self.payload = None
                    self.return_message = str(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                except Exception as e:
                    self.payload = None
                    self.return_message = repr(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST


class TableData(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        if not self.uid:
            self.return_message = "id missing from headers request"
            self.return_code = status.HTTP_400_BAD_REQUEST
        else:
            if self.method == "POST":
                try:
                    self.payload = Profiler.get_data(
                        df=self.working_files[self.uid].data_frame,
                        schema=self.working_files[self.uid].schema,
                        start_index=int(self.json_response['startIndex']),
                        row_count=int(self.json_response['rowCount']),
                        sort_column_index=self.json_response.get(
                            'sortColumnIndexes'),
                        sort_ascending=self.json_response.get('sortAscending',
                                                              True))
                except IDNotFoundError as e:
                    self.payload = None
                    self.return_message = str(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                except PayloadError as e:
                    self.payload = None
                    self.return_message = str(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                except Exception as e:
                    self.payload = None
                    self.return_message = repr(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                    raise e
            elif self.method == "DELETE":
                try:
                    self.working_files.remove(self.uid)
                except IDNotFoundError as e:
                    self.working_files = working_files
                    self.return_message = str(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                except Exception as e:
                    self.working_files = working_files
                    self.return_message = repr(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST


class ColumnAction(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        if not self.uid:
            self.return_message = "id missing from headers request"
            self.return_code = status.HTTP_400_BAD_REQUEST
        else:
            try:
                df, new_schema, action_sequence, insert_indexes = \
                    ColumnHandler.execute(
                        df=self.working_files[self.uid].data_frame,
                        schema=self.working_files[self.uid].schema,
                        payload=self.json_response)
            except IDNotFoundError as e:
                self.return_message = str(e)
                self.return_code = status.HTTP_400_BAD_REQUEST
                return
            except PayloadError as e:
                self.return_message = str(e)
                self.return_code = status.HTTP_400_BAD_REQUEST
                return
            except InvalidDataTypeError as e:
                self.return_message = str(e)
                self.return_code = status.HTTP_400_BAD_REQUEST
                return
            except Exception as e:
                self.return_message = str(e)
                self.return_code = status.HTTP_400_BAD_REQUEST
                return
            try:
                self.working_files.update_df(
                    df=df,
                    uid=self.uid)
            except Exception as e:
                self.return_message = str(e)
                self.return_code = status.HTTP_400_BAD_REQUEST
                return
            if new_schema:
                try:
                    self.working_files.update_schema(uid=self.uid,
                                                     schema=new_schema)
                except Exception as e:
                    self.return_message = str(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                    return
            if action_sequence:
                self.working_files.update_schema(
                    uid=self.uid,
                    action_sequence=action_sequence)
            self.payload = {
                "newColumns": insert_indexes,
                "message": self.return_message,
                "status_code": self.return_code
                }


class TableAction(GenericCall):
    def __init__(self, request, working_files, action=None):
        super().__init__(request=request, working_files=working_files)
        if not self.uid:
            self.return_message = "id missing from headers request"
            self.return_code = status.HTTP_400_BAD_REQUEST
        else:
            if action == 'undo':
                df, new_schema, indexes, remove_indexes = TableHandler.undo(
                    df=self.working_files[self.uid].data_frame,
                    schema=self.working_files[self.uid].schema)
                if not df.empty:
                    self.working_files.update_df(
                        uid=self.uid,
                        df=df)
                if new_schema:
                    self.working_files.update_schema(
                        uid=self.uid,
                        schema=new_schema,)
                self.working_files.update_schema(
                    uid=self.uid,
                    action_sequence='undo')
            else:
                try:
                    self.payload = TableHandler.execute(
                        df=self.working_files[self.uid].data_frame,
                        schema=self.working_files[self.uid].schema,
                        payload=self.json_response,
                        uid=self.uid)
                except IDNotFoundError as e:
                    self.payload = None
                    self.return_message = str(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                    return
                except PayloadError as e:
                    self.payload = None
                    self.return_message = str(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                    return
                except Exception as e:
                    self.payload = None
                    self.return_message = str(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                    return
