def get_error_message(exc: Exception, message: str = None) -> str:
    if message is not None:
        return message
    return exc.args[0] if exc.args and exc.args[0] else repr(exc)
