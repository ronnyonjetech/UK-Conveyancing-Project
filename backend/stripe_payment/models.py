from django.db import models
from django.conf import settings
# Create your models here.

class CheckoutSessionRecord(models.Model):
   
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        help_text="The user who initiated the checkout."
    )
    stripe_customer_id = models.CharField(max_length=255)
    stripe_checkout_session_id = models.CharField(max_length=255)
    stripe_price_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    has_access = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.stripe_checkout_session_id