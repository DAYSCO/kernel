from copy import deepcopy

import pandas as pd
from flask import status
from flask import jsonify

from app.days.actions import Actions
from app.manager import Ingester
from app.days.objects import DaysDataFrame
from app.exceptions import (
    DuplicateNameError,
    InvalidDataTypeError,
    IDNotFoundError,
    PayloadError,
    status_codes, FileParseError
)


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
        self.return_code = 200
        self.working_files = working_files


class UploadFile(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        self.mp_file = request.files.get('file')
        self.file_type = Ingester.identify_file(self.file_name)
        if not self.uid:
            self.payload = {
                'message': "id missing from headers request",
                'status_code': 400,
                'kernel_status_code':
                    status_codes['MissingHeaderAttributeError']
            }
        else:
            try:
                try:
                    size_in_kb = round(int(str(self.file_size)) / 1024, 2)
                except ValueError:
                    size_in_kb = 0.0
                payload = dict(
                    TableName=self.file_name,
                    FileName=self.file_name,
                    SizeInKb=size_in_kb,
                    uid=self.uid
                )
                if self.file_type in ['txt', 'csv', 'json', 'html']:
                    try:
                        data_frame = Ingester.mpfile_upload(
                            mp_file=self.mp_file,
                            file_type=self.file_type,
                            file_name=self.file_name)
                    except FileParseError as e:
                        self.payload = {
                            "message": str(e),
                            "status_code": 400,
                            "kernel_status_code": e.status_code,
                            "errors": [str(e)]
                        }
                        return
                    self.working_files.add(
                        DaysDataFrame(df=data_frame, payload=payload))
                elif self.file_type == 'xlsx' or self.file_type == 'xls':
                    try:
                        sheet_names = pd.ExcelFile(self.mp_file).sheet_names
                    except:
                        raise FileParseError(self.file_name)
                    for index, sheet_name in enumerate(sheet_names):
                        try:
                            data_frame = Ingester.mpfile_upload(
                                mp_file=self.mp_file,
                                file_type=self.file_type,
                                sheet_name=sheet_name,
                                file_name=self.file_name)
                        except FileParseError as e:
                            self.payload = {
                                "message": str(e),
                                "status_code": 400,
                                "kernel_status_code": e.status_code,
                                "errors": [str(e)]
                            }
                            return
                        payload.update(dict(TableName=sheet_name,
                                            sheet_index=index))
                        self.working_files.add(
                            DaysDataFrame(df=data_frame, payload=payload))
                self.payload = {
                    "newColumns": [],
                    "message": self.return_message,
                    "status_code": self.return_code,
                }
            except FileParseError as e:
                self.payload = {
                    "message": str(e),
                    "status_code": 400,
                    "kernel_status_code": e.status_code,
                    "errors": [str(e)]
                }
            except Exception as e:
                self.payload = {
                    "message": str(e),
                    "status_code": 404,
                    "kernel_status_code": status_codes['GeneralError'],
                    "errors": [str(e)]
                }


class ReadFileContents(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        if not self.uid:
            self.payload = {
                'message': "id missing from headers request",
                'status_code': 400,
                'kernel_status_code':
                    status_codes['MissingHeaderAttributeError']
            }
        else:
            try:
                try:
                    size_in_kb = round(int(str(self.file_size)) / 1024, 2)
                except ValueError:
                    size_in_kb = 0.0
                payload = dict(
                    TableName=self.file_name,
                    SizeInKb=size_in_kb,
                    uid=self.uid
                )
                try:
                    data_frame = Ingester.content_upload(
                        contents=self.data,
                        file_name=self.file_name)
                except FileParseError as e:
                    self.payload = {
                        "message": str(e),
                        "status_code": 400,
                        "kernel_status_code": e.status_code,
                        "errors": [str(e)]
                    }
                    return
                self.working_files.add(
                    DaysDataFrame(df=data_frame, payload=payload))
                self.payload = {
                    "newColumns": [],
                    "message": self.return_message,
                    "status_code": self.return_code
                }
            except Exception as e:
                self.payload = {
                    "message": str(e),
                    "status_code": 404,
                    "kernel_status_code": status_codes['GeneralError'],
                    "errors": [str(e)]
                }


class TableSchema(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        if not self.uid:
            self.payload = {
                'message': "id missing from headers request",
                'status_code': 400,
                'kernel_status_code':
                    status_codes['MissingHeaderAttributeError']
            }
        else:
            try:
                self.payload = jsonify(self.working_files[self.uid].schema)
            except IDNotFoundError as e:
                self.payload = {
                    "message": str(e),
                    "status_code": 400,
                    "kernel_status_code": e.status_code,
                    "errors": [str(e)]
                }
                return
            except Exception as e:
                self.payload = {
                    "message": str(e),
                    "status_code": 404,
                    "kernel_status_code": status_codes['GeneralError'],
                    "errors": [str(e)]
                }


class TableData(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        if not self.uid:
            self.payload = {
                'message': "id missing from headers request",
                'status_code': 400,
                'kernel_status_code':
                    status_codes['MissingHeaderAttributeError']
            }
        else:
            if self.method == "POST":
                try:
                    self.payload = self.working_files[self.uid].to_json(
                        row_count=int(self.json_response['rowCount']),
                        start=int(self.json_response['startIndex'])
                    )
                except (IDNotFoundError, PayloadError) as e:
                    self.payload = {
                        "message": str(e),
                        "status_code": 400,
                        "kernel_status_code": e.status_code,
                        "errors": [str(e)]
                    }
                    return
                except Exception as e:
                    self.payload = {
                        "message": str(e),
                        "status_code": 404,
                        "kernel_status_code": status_codes['GeneralError'],
                        "errors": [str(e)]
                    }
            elif self.method == "DELETE":
                try:
                    self.working_files.remove(self.uid)
                except IDNotFoundError as e:
                    self.payload = {
                        "message": str(e),
                        "status_code": 400,
                        "kernel_status_code": e.status_code,
                        "errors": [str(e)]
                    }
                    return
                except Exception as e:
                    self.payload = {
                        "message": str(e),
                        "status_code": 404,
                        "kernel_status_code": status_codes['GeneralError'],
                        "errors": [str(e)]
                    }


class ColumnAction(GenericCall):
    def __init__(self, request, working_files):
        super().__init__(request=request, working_files=working_files)
        if not self.uid:
            self.payload = {
                'message': "id missing from headers request",
                'status_code': 400,
                'kernel_status_code':
                    status_codes['MissingHeaderAttributeError']
            }
        else:
            try:
                ddf = deepcopy(self.working_files[self.uid])
                ddf, payload_res = Actions.execute(
                    ddf=ddf,
                    payload=self.json_response)
            except (PayloadError,
                    InvalidDataTypeError,
                    DuplicateNameError,
                    IDNotFoundError) as e:
                self.payload = {
                    "message": str(e),
                    "errors": [str(e)],
                    'status_code': 400,
                    'kernel_status_code': e.status_code
                }
                return
            except Exception as e:
                self.payload = {
                    "message": str(e),
                    "status_code": 404,
                    "kernel_status_code": status_codes['GeneralError'],
                    "errors": [str(e)]
                }
                return

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
            self.payload = {
                'message': "id missing from headers request",
                'status_code': 400,
                'kernel_status_code':
                    status_codes['MissingHeaderAttributeError']
            }
        else:
            if action == 'undo':
                try:
                    action_sequence = self.working_files[self.uid].action_sequence
                except IDNotFoundError as e:
                    self.payload = {
                        "message": str(e),
                        "errors": [str(e)],
                        'status_code': 400,
                        'kernel_status_code': e.status_code
                    }
                    return
                if len(action_sequence) == 0:
                    return
                ddf = deepcopy(self.working_files[self.uid])
                ddf, payload_res = Actions.execute(
                    ddf=ddf,
                    payload={'action': action})

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
                    self.payload = {
                        "message": str(e),
                        "status_code": 404,
                        "kernel_status_code": status_codes['GeneralError'],
                        "errors": [str(e)]
                    }
                    return
                self.payload = {
                    "message": self.return_message,
                    "status_code": self.return_code,
                    "file_path": payload_res.get('file_path')
                }
