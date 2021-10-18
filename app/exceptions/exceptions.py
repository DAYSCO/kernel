class IDNotFoundError(Exception):
    def __init__(self, uid, message="id does not exist for any existing working files."):
        self.uid = uid
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'({self.uid}) -> {self.message}'

class PayloadError(Exception):
    def __init__(self, key, value, message="error parsing payload"):
        self.key = key
        self.value = value
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'({self.key}: {self.value}) -> {self.message}'


class InvalidDataTypeError(Exception):
    def __init__(self, column, dataType, message="invalid data type for column"):
        self.column = column
        self.message = message
        self.dataType = dataType
        super().__init__(self.message)

    def __str__(self):
        return f'({self.dataType}) -> {self.message} "{self.column}"'