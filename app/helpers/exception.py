from enum import Enum


class ErrorCode(Enum):
    class Error:

        code: int
        message: str

        def __init__(self, code: int, message: str):
            self.code = code
            self.message = message

    UNEXPECTED_ERROR = Error(500, 'Internal Server Error')

    NOT_FOUND_API = Error(404, 'Not Found')


class BaseException(Exception):

    __status_code: int
    __error_code: ErrorCode

    def __init__(self, status_code: int, error_code: ErrorCode):
        self.__status_code = status_code
        self.__error_code = error_code

    def get_status_code(self) -> int:
        return self.__status_code

    def get_error_code(self) -> ErrorCode:
        return self.__error_code.value
