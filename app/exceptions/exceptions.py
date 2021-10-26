status_codes = {
    "IDNotFoundError": 401,
    "MissingHeaderAttributeError": 402,
    "PayloadError": 403,
    "GeneralError": 404,
    "InvalidDataTypeError": 405,
    "MissingPayloadValueError": 406,
    "DuplicateNameError": 407,
    "FileParseError": 408,
}


class IDNotFoundError(Exception):
    def __init__(self, uid,
                 message="id does not exist for any existing working files."):
        self.uid = uid
        self.message = message
        self.status_code = status_codes[self.__class__.__name__]
        super().__init__(self.message)

    def __str__(self):
        return f'({self.uid}) -> {self.message}'


class PayloadError(Exception):
    def __init__(self, key, value, message="error parsing payload"):
        self.key = key
        self.value = value
        self.message = message
        self.status_code = status_codes[self.__class__.__name__]
        super().__init__(self.message)

    def __str__(self):
        return f'({self.key}: {self.value}) -> {self.message}'


class InvalidDataTypeError(Exception):
    def __init__(self, column, data_type,
                 message="invalid data type for column"):
        self.column = column
        self.message = message
        self.dataType = data_type
        self.status_code = status_codes[self.__class__.__name__]
        super().__init__(self.message)

    def __str__(self):
        return f'({self.dataType}) -> {self.message} "{self.column}"'


class MissingHeaderAttributeError(Exception):
    def __init__(self, param, message="missing from headers request"):
        self.message = message
        self.param = param
        self.status_code = status_codes[self.__class__.__name__]
        super().__init__(self.message)

    def __str__(self):
        return f'({self.param}) -> {self.message}'


class MissingPayloadValueError(Exception):
    def __init__(self, param,
                 message="value is missing from payload of request"):
        self.message = message
        self.param = param
        self.status_code = status_codes[self.__class__.__name__]
        super().__init__(self.message)

    def __str__(self):
        return f'({self.param}) -> {self.message}'


class DuplicateNameError(Exception):
    def __init__(self, column,
                 message="can not duplicate the name"):
        self.column = column
        self.message = message
        self.status_code = status_codes[self.__class__.__name__]
        super().__init__(self.message)

    def __str__(self):
        return f'({self.column}) -> {self.message}'


class FileParseError(Exception):
    def __init__(self, file_name,
                 message="Unable to parse the file."):
        self.file_name = file_name
        self.message = message
        self.status_code = status_codes[self.__class__.__name__]
        super().__init__(self.message)

    def __str__(self):
        return f'({self.file_name}) -> {self.message}'
