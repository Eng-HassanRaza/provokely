from django.urls import path
from api_hosted.views import (
    AuthAPIView,
    AIProxyView,
    saas_validator_privacy,
    CreateCheckoutSessionView,
    StripeWebhookView,
    SubscriptionStatusView,
    payment_success,
    payment_cancel,
    extension_privacy,
    extension_support,
    cart_recovery_report,
    cart_recovery_infographic
)

app_name = 'api_hosted'

urlpatterns = [
    path('auth', AuthAPIView.as_view(), name='auth'),
    path('ai', AIProxyView.as_view(), name='ai'),
    path('saas-validator-privacy', saas_validator_privacy, name='saas_validator_privacy'),
    path('create-checkout-session', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('subscription-status', SubscriptionStatusView.as_view(), name='subscription_status'),
    path('success', payment_success, name='payment_success'),
    path('cancel', payment_cancel, name='payment_cancel'),
    path('privacy', extension_privacy, name='extension_privacy'),
    path('support', extension_support, name='extension_support'),
    path('cart-recovery-report', cart_recovery_report, name='cart_recovery_report'),
    path('cart-recovery-infographic', cart_recovery_infographic, name='cart_recovery_infographic'),
]

