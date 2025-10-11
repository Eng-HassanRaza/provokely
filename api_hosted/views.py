import jwt as pyjwt
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from api_hosted.models import APIUser
from api_hosted.serializers import (
    AuthRequestSerializer,
    AuthResponseSerializer,
    AIRequestSerializer,
    AIResponseSerializer
)
from api_hosted.services import JWTService, AIProxyService
from api_hosted.authentication import JWTAuthentication


class AuthAPIView(APIView):
    """
    POST /api/auth - Email-based authentication
    Creates or authenticates users with email only (no password)
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AuthRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'message': 'Invalid request',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        
        try:
            # Find or create user
            api_user, created = APIUser.objects.get_or_create(
                email=email,
                defaults={
                    'id': APIUser.generate_user_id()
                }
            )
            
            # Generate JWT token
            auth_token = JWTService.generate_token(api_user.id, api_user.email)
            
            # Update user's token in database
            api_user.auth_token = auth_token
            api_user.save()
            
            # Prepare response
            response_data = {
                'authToken': auth_token,
                'userId': api_user.id,
                'message': 'Authentication successful'
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': 'Authentication failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIProxyView(APIView):
    """
    POST /api/ai - AI proxy endpoint with usage tracking
    Routes AI requests through backend with authentication and usage tracking
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    
    def post(self, request):
        # Validate request
        serializer = AIRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'message': 'Invalid request',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        prompt = serializer.validated_data['prompt']
        user_email = serializer.validated_data['userEmail']
        options = serializer.validated_data.get('options', {})
        
        # Get authenticated user from request (set by JWTAuthentication)
        api_user = request.user
        
        # Verify email matches
        if api_user.email != user_email:
            return Response({
                'message': 'Email mismatch with authenticated user'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Initialize AI service
            ai_service = AIProxyService()
            
            # Get model and max tokens from options
            model = options.get('model', 'gpt-4o-mini')
            max_tokens = options.get('maxTokens', 4000)
            
            # Call OpenAI API
            result = ai_service.call_openai(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens
            )
            
            # Calculate cost
            cost = ai_service.calculate_cost(
                tokens_used=result['tokens_used'],
                model=result['model']
            )
            
            # Track usage
            ai_service.track_usage(
                api_user=api_user,
                action='ai_generation',
                tokens_used=result['tokens_used'],
                cost=cost,
                model=result['model'],
                prompt_length=len(prompt)
            )
            
            # Return response
            response_data = {
                'response': result['response'],
                'tokensUsed': result['tokens_used'],
                'cost': float(cost)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                'message': 'AI request failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def saas_validator_privacy(request):
    """
    Privacy policy page for SaaS Validator Chrome Extension
    Public page - no authentication required
    """
    return render(request, 'saas_validator_privacy.html')

