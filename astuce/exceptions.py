class AstuceError(Exception):
    """Base exception for the Astuce library."""


class AstuceAPIError(AstuceError):
    """Raised when the API returns a non-2xx HTTP response."""

    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        super().__init__(f"API error HTTP {status_code}: {message}")


class AstuceNetworkError(AstuceError):
    """Raised on network failure (timeout, DNS error, connection refused…)."""


class AstuceParseError(AstuceError):
    """Raised when the API response cannot be parsed as JSON."""
