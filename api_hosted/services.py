import jwt
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from api_hosted.models import APIUser, UsageLog
import stripe
from stripe import StripeError, SignatureVerificationError


class JWTService:
    """Handle JWT token generation and verification"""
    
    @staticmethod
    def get_secret_key():
        """Get JWT secret key from settings"""
        return getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
    
    @staticmethod
    def generate_token(user_id, email):
        """
        Generate JWT token for user
        
        Args:
            user_id: User ID
            email: User email
        
        Returns:
            str: JWT token
        """
        payload = {
            'userId': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            JWTService.get_secret_key(),
            algorithm='HS256'
        )
        
        return token
    
    @staticmethod
    def verify_token(token):
        """
        Verify JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            dict: Decoded payload if valid
        
        Raises:
            jwt.ExpiredSignatureError: If token expired
            jwt.InvalidTokenError: If token invalid
        """
        try:
            payload = jwt.decode(
                token,
                JWTService.get_secret_key(),
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError('Token has expired')
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError('Invalid token')


class AIProxyService:
    """Handle AI API calls and usage tracking"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.default_model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
        
        if not self.api_key:
            raise ValueError('OPENAI_API_KEY not configured in settings')
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError('openai package not installed')
    
    def call_openai(self, prompt, model=None, max_tokens=4000):
        """
        Call OpenAI API
        
        Args:
            prompt: User prompt
            model: Model name (optional)
            max_tokens: Max tokens to generate
        
        Returns:
            dict: Response with content, tokens_used
        """
        model = model or self.default_model
        
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            
            response_text = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens
            
            return {
                'response': response_text,
                'tokens_used': tokens_used,
                'model': model
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def calculate_cost(self, tokens_used, model='gpt-4o-mini'):
        """
        Calculate cost based on tokens and model
        
        Args:
            tokens_used: Number of tokens used
            model: Model name
        
        Returns:
            float: Cost in USD
        """
        # Pricing per 1M tokens (as of 2024)
        pricing = {
            'gpt-4o-mini': 0.15,  # $0.15 per 1M tokens
            'gpt-4o': 2.50,       # $2.50 per 1M tokens
            'gpt-4': 30.00,       # $30 per 1M tokens
            'gpt-3.5-turbo': 0.50 # $0.50 per 1M tokens
        }
        
        rate = pricing.get(model, 0.15)
        cost = (tokens_used / 1_000_000) * rate
        
        return round(cost, 4)
    
    def track_usage(self, api_user, action, tokens_used, cost, model, prompt_length):
        """
        Track API usage in database
        
        Args:
            api_user: APIUser instance
            action: Action name
            tokens_used: Tokens used
            cost: Cost in USD
            model: Model name
            prompt_length: Length of prompt
        """
        # Create usage log
        UsageLog.objects.create(
            api_user=api_user,
            action=action,
            tokens_used=tokens_used,
            cost=cost,
            model=model,
            prompt_length=prompt_length
        )
        
        # Update user totals
        api_user.total_requests += 1
        api_user.total_tokens_used += tokens_used
        api_user.total_cost += Decimal(str(cost))
        api_user.save()


class StripeService:
    """Handle Stripe payment operations"""
    
    def __init__(self):
        self.stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
        if self.stripe_key:
            stripe.api_key = self.stripe_key
        
        self.monthly_price_id = getattr(settings, 'STRIPE_MONTHLY_PRICE_ID', None)
        self.annual_price_id = getattr(settings, 'STRIPE_ANNUAL_PRICE_ID', None)
        self.webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    
    def create_checkout_session(self, email, plan='monthly', success_url=None, cancel_url=None):
        """
        Create Stripe checkout session
        
        Args:
            email: Customer email
            plan: 'monthly' or 'annual'
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel
        
        Returns:
            dict: Session data with session_id and url
        """
        if not self.stripe_key:
            raise ValueError('STRIPE_SECRET_KEY not configured')
        
        price_id = self.annual_price_id if plan == 'annual' else self.monthly_price_id
        
        if not price_id:
            raise ValueError(f'Stripe price ID not configured for {plan} plan')
        
        # Default URLs if not provided
        if not success_url:
            success_url = 'https://provokely.com/success?session_id={CHECKOUT_SESSION_ID}'
        if not cancel_url:
            cancel_url = 'https://provokely.com/cancel'
        
        try:
            session = stripe.checkout.Session.create(
                customer_email=email,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'userEmail': email,
                    'plan': plan
                }
            )
            
            return {
                'sessionId': session.id,
                'url': session.url
            }
        except StripeError as e:
            raise Exception(f'Stripe error: {str(e)}')
    
    def verify_webhook_signature(self, payload, signature):
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Raw request body
            signature: Stripe signature header
        
        Returns:
            Event object if valid
        
        Raises:
            ValueError: If signature invalid
        """
        if not self.webhook_secret:
            raise ValueError('STRIPE_WEBHOOK_SECRET not configured')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
        except ValueError as e:
            raise ValueError(f'Invalid payload: {str(e)}')
        except SignatureVerificationError as e:
            raise ValueError(f'Invalid signature: {str(e)}')
    
    def handle_checkout_completed(self, session):
        """
        Handle successful checkout
        
        Args:
            session: Stripe checkout session object
        """
        customer_email = session.get('customer_email') or session.get('metadata', {}).get('userEmail')
        subscription_id = session.get('subscription')
        customer_id = session.get('customer')
        
        if not customer_email:
            raise ValueError('No customer email found in session')
        
        try:
            api_user = APIUser.objects.get(email=customer_email)
            api_user.is_pro = True
            api_user.subscription_id = subscription_id
            api_user.stripe_customer_id = customer_id
            api_user.save()
            
            return api_user
        except APIUser.DoesNotExist:
            raise ValueError(f'User not found: {customer_email}')
    
    def handle_subscription_deleted(self, subscription):
        """
        Handle subscription cancellation
        
        Args:
            subscription: Stripe subscription object
        """
        subscription_id = subscription.get('id')
        
        if not subscription_id:
            raise ValueError('No subscription ID found')
        
        try:
            api_user = APIUser.objects.get(subscription_id=subscription_id)
            api_user.is_pro = False
            api_user.save()
            
            return api_user
        except APIUser.DoesNotExist:
            raise ValueError(f'User not found with subscription: {subscription_id}')
    
    def get_subscription_status(self, email):
        """
        Get user's subscription status
        
        Args:
            email: User email
        
        Returns:
            dict: Subscription status with isPro and projectsRemaining
        """
        try:
            api_user = APIUser.objects.get(email=email)
            return {
                'isPro': api_user.is_pro,
                'projectsRemaining': api_user.projects_remaining
            }
        except APIUser.DoesNotExist:
            raise ValueError(f'User not found: {email}')

