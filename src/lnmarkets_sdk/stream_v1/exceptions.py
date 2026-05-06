"""Stream V1 error classes."""


class StreamDisconnectedError(Exception):
    def __init__(self, method: str) -> None:
        super().__init__(f"Cannot call {method}(): WebSocket is not connected")
        self.name = "StreamDisconnectedError"


class StreamRequestTimeoutError(Exception):
    def __init__(self, method: str) -> None:
        super().__init__(f"Request timed out after 10s (method: {method})")
        self.name = "StreamRequestTimeoutError"
        self.method = method


class StreamRpcError(Exception):
    def __init__(self, code: int, message: str, data: object | None = None) -> None:
        super().__init__(message)
        self.name = "StreamRpcError"
        self.code = code
        self.data = data


class ReconnectFailedError(Exception):
    def __init__(self, attempts: int) -> None:
        super().__init__(f"WebSocket reconnect failed after {attempts} attempt(s)")
        self.name = "ReconnectFailedError"
        self.attempts = attempts
