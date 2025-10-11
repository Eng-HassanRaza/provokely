from django.urls import path
from api_hosted.views import (
    AuthAPIView,
    AIProxyView,
    saas_validator_privacy,
    CreateCheckoutSessionView,
    StripeWebhookView,
    SubscriptionStatusView
)

app_name = 'api_hosted'

urlpatterns = [
    path('auth', AuthAPIView.as_view(), name='auth'),
    path('ai', AIProxyView.as_view(), name='ai'),
    path('saas-validator-privacy', saas_validator_privacy, name='saas_validator_privacy'),
    path('create-checkout-session', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('subscription-status', SubscriptionStatusView.as_view(), name='subscription_status'),
]

