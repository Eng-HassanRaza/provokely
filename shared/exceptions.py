"""
Custom exceptions for the application
"""


class ProvokelyException(Exception):
    """Base exception for Provokely"""
    pass


class PlatformAPIError(ProvokelyException):
    """Exception for platform API errors"""
    pass


class AuthenticationError(ProvokelyException):
    """Exception for authentication errors"""
    pass


class SentimentAnalysisError(ProvokelyException):
    """Exception for sentiment analysis errors"""
    pass


class ResponseGenerationError(ProvokelyException):
    """Exception for response generation errors"""
    pass


class ValidationError(ProvokelyException):
    """Exception for validation errors"""
    pass
