"""
Standard API response helpers for mobile app consumption
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response


def success_response(data=None, message="Operation successful", status_code=200):
    """
    Standard success response format
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
    
    Returns:
        Response: DRF Response object
    """
    return Response({
        'success': True,
        'data': data,
        'message': message
    }, status=status_code)


def error_response(message, code="ERROR", details=None, status_code=400):
    """
    Standard error response format
    
    Args:
        message: Error message
        code: Error code
        details: Additional error details
        status_code: HTTP status code
    
    Returns:
        Response: DRF Response object
    """
    return Response({
        'success': False,
        'error': {
            'code': code,
            'message': message,
            'details': details
        }
    }, status=status_code)


def paginated_response(data, count, next_url=None, previous_url=None, message="Data retrieved successfully"):
    """
    Standard paginated response format
    
    Args:
        data: List of items
        count: Total count
        next_url: URL for next page
        previous_url: URL for previous page
        message: Success message
    
    Returns:
        Response: DRF Response object
    """
    return Response({
        'success': True,
        'data': {
            'results': data,
            'count': count,
            'next': next_url,
            'previous': previous_url
        },
        'message': message
    }, status=200)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    
    Converts all exceptions to our standard error format
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'error': {
                'code': exc.__class__.__name__,
                'message': str(exc),
                'details': response.data
            }
        }
        response.data = custom_response_data
    
    return response
