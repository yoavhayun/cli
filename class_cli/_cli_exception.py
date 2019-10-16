class CLIException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)

    def _join_msg(self, prefix, message=None):
        return prefix if message is None else "{}: {}".format(prefix, message)


class CompilationException(CLIException):
    def __init__(self, message): super(Exception, self).__init__(self._join_msg("Failed to compile CLI class", message))

class InitializationException(CLIException):
    def __init__(self, message): super(Exception, self).__init__(self._join_msg("Failed to initialize CLI instance", message))

class InputException(CLIException):
    def __init__(self, message): super(Exception, self).__init__(self._join_msg("CLI Failed to execute input", message))

class InternalException(CLIException):
    def __init__(self, message): super(Exception, self).__init__(self._join_msg("CLI Internal Exception", message))