"""Custom exception classes."""
from fastapi import HTTPException, status


class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, resource: str, resource_id: str = ""):
        msg = f"{resource} not found" + (f": {resource_id}" if resource_id else "")
        super().__init__(msg, status_code=404)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class ConflictException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class ValidationException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class LLMException(AppException):
    def __init__(self, message: str = "LLM call failed"):
        super().__init__(message, status_code=503)


class InterviewException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)
