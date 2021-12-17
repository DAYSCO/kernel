import codecs
import logging

from datetime import datetime
from flask import Blueprint, request, make_response
from app.config import Config
from app.controllers import ActiveWorkingFiles
from app.resources import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '-- %(asctime)s %(name)-10s %(levelname)-5s %(message)s')
file_handler = logging.FileHandler(
    f"{Config.LOG_PATH}/{datetime.now().strftime('%Y-%m-%d_%H%M')}.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app_bp = Blueprint('api', __name__, )

global working_files
working_files = ActiveWorkingFiles()


@app_bp.route('/')
def index():
    return 'DAYS KERNEL API', 200


@app_bp.route('/api/v1/upload-file', methods=['POST'])
def upload_file():
    logger.info(f"'upload-file' POST request, {request.remote_addr}")
    if not request.files.get('file'):
        logger.info(f"File not in request.")
    global working_files
    request_obj = UploadFile(
        request=request,
        working_files=working_files)
    working_files = request_obj.working_files
    logger.info(f"{request_obj.return_message} {request_obj.return_code}")
    if request_obj.payload:
        return request_obj.payload, request_obj.return_code
    else:
        return request_obj.return_message, request_obj.return_code


@app_bp.route('/api/v1/read-file-contents', methods=['POST'])
def read_file_contents():
    logger.info(f"'read-file-contents' POST request, {request.remote_addr}")
    global working_files
    request_obj = ReadFileContents(
        request=request,
        working_files=working_files)
    working_files = request_obj.working_files
    logger.info(f"{request_obj.return_message} {request_obj.return_code}")
    if request_obj.payload:
        return request_obj.payload, request_obj.return_code
    else:
        return request_obj.return_message, request_obj.return_code


@app_bp.route('/api/v1/table/info', methods=['GET'])
def table_schema():
    logger.info(
        f"'set_table_schema' {request.method} request, {request.remote_addr}")
    global working_files
    request_obj = TableSchema(
        request=request,
        working_files=working_files)
    logger.info(f"{request_obj.return_message} {request_obj.return_code}")
    if request_obj.method == "GET" and request_obj.payload:
        return request_obj.payload, request_obj.return_code
    else:
        return request_obj.return_message, request_obj.return_code


@app_bp.route('/api/v1/column/action', methods=['PUT'])
def perform_column_action():
    logger.info(f"'perform_column_action' PUT request, {request.remote_addr}")
    global working_files
    request_obj = ColumnAction(
        request=request,
        working_files=working_files)
    working_files = request_obj.working_files
    logger.info(f"{request_obj.return_message} {request_obj.return_code}")
    if request_obj.payload:
        return request_obj.payload, request_obj.return_code
    else:
        return request_obj.return_message, request_obj.return_code


@app_bp.route('/api/v1/column/bulk-action', methods=['PUT'])
def perform_bulk_column_action():
    logger.info(f"'perform_column_action' PUT request, {request.remote_addr}")
    global working_files
    request_obj = BulkColumnAction(
        request=request,
        working_files=working_files)
    working_files = request_obj.working_files
    logger.info(f"{request_obj.return_message} {request_obj.return_code}")
    if request_obj.payload:
        return request_obj.payload, request_obj.return_code
    else:
        return request_obj.return_message, request_obj.return_code


@app_bp.route('/api/v1/table/action', methods=['POST'])
def perform_table_action():
    logger.info(f"'perform_table_action' POST request, {request.remote_addr}")
    global working_files
    request_obj = TableAction(
        request=request,
        working_files=working_files)
    working_files = request_obj.working_files
    logger.info(f"{request_obj.return_message} {request_obj.return_code}")
    if request_obj.payload:
        return request_obj.payload, request_obj.return_code
    else:
        return request_obj.return_message, request_obj.return_code


@app_bp.route('/api/v1/table/content', methods=['GET'])
def get_table_content():
    logger.info(f"'get_table_content' POST request, {request.remote_addr}")
    global working_files
    request_obj = TableAction(
        request=request,
        working_files=working_files)
    working_files = request_obj.working_files
    logger.info(f"{request_obj.return_message} {request_obj.return_code}")
    file_path = request_obj.payload.get('file_path')
    file_data = codecs.open(file_path, 'rb').read()
    response = make_response()
    response.data = file_data
    return response


@app_bp.route('/api/v1/table/data', methods=['POST', 'DELETE'])
def table_data():
    logger.info(
        f"'get_table_data' {request.method} request, {request.remote_addr}")
    global working_files
    try:
        request_obj = TableData(
            request=request,
            working_files=working_files)
    except Exception as e:
        raise e
    logger.info(f"{request_obj.return_message} {request_obj.return_code}")
    if request_obj.payload:
        return request_obj.payload, request_obj.return_code
    else:
        return request_obj.return_message, request_obj.return_code


@app_bp.route('/api/v1/table/undo', methods=['GET', 'PUT'])
def undo_action():
    logger.info(f"'perform undo action' "
                f"{request.method} request, {request.remote_addr}")
    global working_files
    request_obj = TableAction(
        request=request,
        working_files=working_files,
        action='undo')
    logger.info(f"{request_obj.return_message} {request_obj.return_code}")
    if request_obj.payload:
        return request_obj.payload, request_obj.return_code
    else:
        return request_obj.return_message, request_obj.return_code


@app_bp.route('/api/v1/address/validate', methods=['POST'])
def validation_action():
    logger.info(f"'perform address validation action' "
                f"{request.method} request, {request.remote_addr}")
    request_obj = ValidationAction(request=request)
    logger.info(f"{request_obj.return_message} {request_obj.return_code}")
    if request_obj.payload:
        return request_obj.payload, request_obj.return_code
    else:
        return request_obj.return_message, request_obj.return_code


@app_bp.route('/api/v2/address/validate', methods=['POST'])
def address_validation_action():
    logger.info(f"'perform address validation action' "
                f"{request.method} request, {request.remote_addr}")
    request_obj = ValidationAction(request=request, version='v2')
    logger.info(f"{request_obj.return_message} {request_obj.return_code}")
    if request_obj.payload:
        return request_obj.payload, request_obj.return_code
    else:
        return request_obj.return_message, request_obj.return_code
