import jwt as pyjwt
from django.shortcuts import render
from django.conf import settings
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
from api_hosted.services import JWTService, AIProxyService, StripeService
from api_hosted.authentication import JWTAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


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
            
            # Prepare response with subscription info
            response_data = {
                'authToken': auth_token,
                'userId': api_user.id,
                'isPro': api_user.is_pro,
                'projectsRemaining': api_user.projects_remaining,
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
        is_new_project = request.data.get('isNewProject', False)
        
        # Get authenticated user from request (set by JWTAuthentication)
        api_user = request.user
        
        # Verify email matches
        if api_user.email != user_email:
            return Response({
                'message': 'Email mismatch with authenticated user'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if user has projects remaining (unless Pro)
        if not api_user.is_pro and is_new_project:
            if api_user.projects_remaining <= 0:
                return Response({
                    'message': 'No free validations remaining. Please upgrade to Pro.',
                    'error': 'LIMIT_REACHED'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Decrement projects remaining
            api_user.projects_remaining -= 1
            api_user.save()
        
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


def payment_success(request):
    """Payment success page"""
    session_id = request.GET.get('session_id', '')
    return render(request, 'payment_success.html', {
        'session_id': session_id
    })


def payment_cancel(request):
    """Payment cancelled page"""
    return render(request, 'payment_cancel.html')


def extension_privacy(request):
    """Privacy policy page for extension"""
    return render(request, 'extension_privacy.html')


def extension_support(request):
    """Support page for extension"""
    return render(request, 'extension_support.html')


class CreateCheckoutSessionView(APIView):
    """
    POST /api/create-checkout-session
    Create Stripe checkout session for subscription
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        plan = request.data.get('plan', 'monthly')  # 'monthly' or 'annual'
        success_url = request.data.get('success_url')
        cancel_url = request.data.get('cancel_url')
        
        if not email:
            return Response({
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if plan not in ['monthly', 'annual']:
            return Response({
                'message': 'Invalid plan. Must be "monthly" or "annual"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            stripe_service = StripeService()
            session_data = stripe_service.create_checkout_session(
                email=email,
                plan=plan,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            return Response(session_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                'message': 'Failed to create checkout session',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    POST /api/stripe-webhook
    Handle Stripe webhook events
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = []  # Disable DRF parsers to get raw body
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        if not sig_header:
            return Response({
                'message': 'Missing Stripe signature'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            stripe_service = StripeService()
            event = stripe_service.verify_webhook_signature(payload, sig_header)
            
            event_type = event['type']
            
            if event_type == 'checkout.session.completed':
                session = event['data']['object']
                try:
                    stripe_service.handle_checkout_completed(session)
                    customer_email = session.get('customer_email') or session.get('customer_details', {}).get('email')
                    print(f"✅ User upgraded to Pro: {customer_email}")
                except Exception as e:
                    print(f"⚠️  Error upgrading user: {str(e)}")
            
            elif event_type == 'customer.subscription.deleted':
                subscription = event['data']['object']
                try:
                    stripe_service.handle_subscription_deleted(subscription)
                    print(f"❌ Subscription cancelled: {subscription.get('id')}")
                except Exception as e:
                    print(f"⚠️  Error cancelling subscription: {str(e)}")
            
            return Response({'received': True}, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': 'Webhook processing failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubscriptionStatusView(APIView):
    """
    GET /api/subscription-status
    Check user's subscription status
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        email = request.query_params.get('email')
        
        if not email:
            return Response({
                'message': 'Email parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            stripe_service = StripeService()
            status_data = stripe_service.get_subscription_status(email)
            
            return Response(status_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': 'Failed to fetch subscription status',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

