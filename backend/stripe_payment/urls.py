from django.urls import path
from .views import StripeCheckoutView,StripeWebhookView,SubscriptionStatusView

urlpatterns=[
    path('create-checkout-session',StripeCheckoutView.as_view()),
    #  path('webhook/', stripe_webhook, name='stripe-webhook'),
    path('webhook', StripeWebhookView.as_view()),
    path('subscription/status/', SubscriptionStatusView.as_view(), name='subscription-status'),
]