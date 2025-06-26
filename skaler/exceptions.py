class SkalerError(Exception):
    """
    Base class for all exceptions raised by Skaler.
    """
    def __init__(self, message=None):
        super().__init__(message or "An unknown Skaler error occured")


class NoAvailableProviders(SkalerError):
    """
    Raised when no providers are available or all have been blocked
    due to rate limits or request failures.
    """
    def __init__(self, message=None):
        super().__init__(message or "No providers are available or all are blocked.")


class ProviderBlocked(SkalerError):
    """
    Raised when a request is attempted using a provider that is currently blocked.

    Attributes:
        provider_name (str): The name or identifier of the blocked provider.
    """
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        super().__init__(f"Provider '{provider_name}' is currently blocked.")


class RequestFailed(SkalerError):
    """
    Raised when an HTTP request to an API provider fails in a non-retryable way.

    Attributes:
        provider_name (str): The name of the provider that failed.
        status_code (int, optional): The HTTP status code returned by the API.
        reason (str, optional): A description or message about why the request failed.
    """
    def __init__(self, provider_name: str, status_code: int = None, reason: str = None):
        self.provider_name = provider_name
        self.status_code = status_code
        self.reason = reason
        msg = f"Request failed for provider '{provider_name}'"
        if status_code:
            msg += f" with status code {status_code}"
        else:
            msg += f": {reason}"

        super().__init__(msg)


class ProxyError(SkalerError):
    """
    Raised when a proxy server fails repeatedly or is deemed unsuable.

    Attributes:
        proxy (str): The proxy address that caused the failure.
        reason (str, optional): A description of the error.
    """
    def __init__(self, proxy: str, reason: str = None):
        self.proxy = proxy
        self.reason = reason
        msg = f"Proxy '{proxy}' failed"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
