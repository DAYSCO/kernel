import pandas as pd
from flask_api import status
from flask import jsonify

from app.days.actions import Actions
from app.manager import Ingester
from app.days.objects import DaysDataFrame
from copy import deepcopy
from app.exceptions import IDNotFoundError, PayloadError


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
                payload = dict(
                    TableName=self.file_name,
                    SizeInKb=self.file_size,
                    uid=self.uid
                )
                if self.file_type in ['txt', 'csv', 'json', 'html']:
                    data_frame = Ingester.mpfile_upload(
                        mp_file=self.mp_file,
                        file_type=self.file_type)
                    self.working_files.add(
                        DaysDataFrame(df=data_frame, payload=payload))
                elif self.file_type == 'xlsx' or self.file_type == 'xls':
                    sheet_names = pd.ExcelFile(self.mp_file).sheet_names
                    for index, sheet_name in enumerate(sheet_names):
                        data_frame = Ingester.mpfile_upload(
                            mp_file=self.mp_file,
                            file_type=self.file_type,
                            sheet_name=sheet_name)
                        payload.update(dict(TableName=sheet_name,
                                            sheet_index=index))
                        self.working_files.add(
                            DaysDataFrame(df=data_frame, payload=payload))
                self.payload = {
                    "newColumns": [],
                    "message": self.return_message,
                    "status_code": self.return_code,
                }
            except Exception as e:
                self.working_files = working_files
                self.return_message = repr(e)
                self.return_code = status.HTTP_400_BAD_REQUEST
                self.payload = {
                    "message": self.return_message,
                    "status_code": self.return_code,
                    "errors": [self.return_message]
                }


class ReadFileContents(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        if not self.uid:
            self.return_message = "id missing from headers request"
            self.return_code = status.HTTP_400_BAD_REQUEST
        else:
            try:
                payload = dict(
                    TableName=self.file_name,
                    SizeInKb=self.file_size,
                    uid=self.uid
                )
                data_frame = Ingester.content_upload(self.data)
                self.working_files.add(
                    DaysDataFrame(df=data_frame, payload=payload))
                self.payload = {
                    "newColumns": [],
                    "message": self.return_message,
                    "status_code": self.return_code
                }

            except Exception as e:
                self.working_files = working_files
                self.return_message = repr(e)
                self.return_code = status.HTTP_400_BAD_REQUEST
                self.payload = {
                    "message": self.return_message,
                    "status_code": self.return_code,
                    "errors": [self.return_message]
                }


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
                    self.return_message = str(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                    self.payload = {
                        'errors': self.return_code,
                        'status_code': self.return_code,
                        'message': self.return_message
                    }
                except Exception as e:
                    self.return_message = repr(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                    self.payload = {
                        'errors': self.return_code,
                        'status_code': self.return_code,
                        'message': self.return_message
                    }


class TableData(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        if not self.uid:
            self.return_message = "id missing from headers request"
            self.return_code = status.HTTP_400_BAD_REQUEST
        else:
            if self.method == "POST":
                try:
                    self.payload = self.working_files[self.uid].to_json(
                        row_count=int(self.json_response['rowCount']),
                        start=int(self.json_response['startIndex'])
                    )
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
                ddf = deepcopy(self.working_files[self.uid])
                ddf, payload_res = Actions.execute(
                    ddf=ddf,
                    payload=self.json_response)
            except Exception as e:
                self.return_message = str(e)
                self.return_code = status.HTTP_400_BAD_REQUEST
                self.payload = {
                    "message": self.return_message,
                    "status_code": self.return_code,
                    "errors": [self.return_message]
                }
                return
            errors = payload_res.get('errors')
            if len(errors):
                self.return_message = str(errors[-1])
                self.return_code = status.HTTP_400_BAD_REQUEST
                self.payload = {
                    "message": self.return_message,
                    "status_code": errors[-1],
                    "errors": errors
                }

            new_columns = payload_res.get('new_columns')
            action = payload_res.get('action')
            self.working_files.add(ddf)
            if action:
                ddf.update_action_sequence(action=action)
            self.payload = {
                "newColumns": new_columns,
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
                if len(self.working_files[self.uid].action_sequence) == 0:
                    return
                ddf = deepcopy(self.working_files[self.uid])
                ddf, payload_res = Actions.execute(
                    ddf=ddf,
                    payload={'action': action})
                errors = payload_res.get('errors')
                if len(errors):
                    self.return_message = str(errors[-1])
                    self.return_code = status.HTTP_400_BAD_REQUEST
                    self.payload = {
                        "message": self.return_message,
                        "status_code": self.return_code,
                        "errors": errors
                    }
                    return

                self.working_files.add(ddf)
                ddf.update_action_sequence()
                self.payload = {
                    "message": self.return_message,
                    "status_code": self.return_code
                }
            else:
                try:
                    ddf, payload_res = Actions.execute(
                        ddf=self.working_files[self.uid],
                        payload=self.json_response)
                except Exception as e:
                    self.return_message = str(e)
                    self.return_code = status.HTTP_400_BAD_REQUEST
                    self.payload = {
                        "message": self.return_message,
                        "status_code": self.return_code,
                        "errors": [str(e)]
                    }
                    return
                errors = payload_res.get('errors')
                if len(errors):
                    self.return_message = str(errors[-1])
                    self.return_code = status.HTTP_400_BAD_REQUEST
                    self.payload = {
                        "message": self.return_message,
                        "status_code": self.return_code,
                        "errors": errors
                    }
                    return
                self.payload = {
                    "message": self.return_message,
                    "status_code": self.return_code,
                    "file_path": payload_res.get('file_path')
                }