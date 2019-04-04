class SystemException(Exception):

    def __init__(self, message, errorcode):
        super(SystemException, self).__init__(message)
        self.errorcode = errorcode


class BusinessException(SystemException):

    def __init__(self, message, errorcode=100):
        super(BusinessException, self).__init__(message=message, errorcode=errorcode)


class DataException(SystemException):

    def __init__(self, message, errorcode=400):
        super(DataException, self).__init__(message=message, errorcode=errorcode)


class ContextException(SystemException):
    def __init__(self, message, errorcode=500):
        super(ContextException, self).__init__(message=message, errorcode=errorcode)


class FileException(SystemException):
    def __init__(self, message, errorcode=404):
        super(FileException, self).__init__(message=message, errorcode=errorcode)