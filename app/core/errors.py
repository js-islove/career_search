from typing import Any, Dict, List, Optional


class PlatformError(Exception):
    """Base exception for all domain errors."""
    code: str = "internal_error"
    status_code: int = 500

    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or []


class NotFoundError(PlatformError):
    code = "not_found"
    status_code = 404


class ValidationError(PlatformError):
    code = "invalid_parameter"
    status_code = 400


class ConflictError(PlatformError):
    code = "conflict"
    status_code = 409


class UnauthorizedError(PlatformError):
    code = "unauthorized"
    status_code = 401


class SSRFSecurityException(PlatformError):
    code = "forbidden_url"
    status_code = 403


class RateLimitExceededException(PlatformError):
    code = "rate_limited"
    status_code = 429


class CircuitOpenException(PlatformError):
    code = "circuit_open"
    status_code = 503


def make_error_envelope(
    code: str,
    message: str,
    details: Optional[List[Dict[str, Any]]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Formats an error response following the RFC 7807 problem details convention."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "request_id": request_id or "unknown",
        }
    }