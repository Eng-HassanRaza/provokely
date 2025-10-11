import jwt as pyjwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api_hosted.models import APIUser
from api_hosted.services import JWTService


class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication for hosted API
    Verifies Bearer token in Authorization header
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            raise AuthenticationFailed('No authorization token provided')
        
        # Extract token from "Bearer <token>"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise AuthenticationFailed('Invalid authorization header format')
        
        token = parts[1]
        
        try:
            # Verify and decode token
            payload = JWTService.verify_token(token)
            
            # Get user from database
            user_id = payload.get('userId')
            email = payload.get('email')
            
            if not user_id or not email:
                raise AuthenticationFailed('Invalid token payload')
            
            try:
                api_user = APIUser.objects.get(id=user_id, email=email)
            except APIUser.DoesNotExist:
                raise AuthenticationFailed('User not found')
            
            # Return user and token
            return (api_user, token)
            
        except pyjwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except pyjwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def authenticate_header(self, request):
        """
        Return WWW-Authenticate header for 401 responses
        """
        return 'Bearer realm="api"'

