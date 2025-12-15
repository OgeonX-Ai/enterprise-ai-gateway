from fastapi import HTTPException, status


class GatewayException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class PolicyViolation(GatewayException):
    def __init__(self, detail: str = "Request rejected by policy"):
        super().__init__(detail, status.HTTP_429_TOO_MANY_REQUESTS)
