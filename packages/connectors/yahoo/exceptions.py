class YahooConnectorError(RuntimeError):
    pass


class YahooTimeoutError(YahooConnectorError):
    pass


class YahooDataError(YahooConnectorError):
    pass

