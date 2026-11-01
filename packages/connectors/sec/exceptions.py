class SecConnectorError(RuntimeError):
    pass


class SecRateLimitError(SecConnectorError):
    pass


class SecUnavailableError(SecConnectorError):
    pass
