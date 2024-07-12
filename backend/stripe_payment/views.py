
from django.conf import settings
import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CheckoutSessionRecord
from rest_framework import status
from django.shortcuts import redirect
from django.views import View
from django.http import JsonResponse
import stripe
import logging
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime
# This is your test secret API key.
stripe.api_key = settings.STRIPE_SECRET_KEY
# Set up logging
logger = logging.getLogger(__name__)
# class StripeCheckoutView(APIView):
#     def post(self,request):
#         try:
#             checkout_session = stripe.checkout.Session.create(
#                 payment_method_types=['card'],
#                 line_items=[
#                     # {
#                     #     'price':'price_1PCL0GFvgrkbd3pbmUM5wSjB',
#                     #     'quantity':1,
#                     # },
#                      {
#                         'price':'price_1PHkrwFvgrkbd3pbXVkZ8nAP',
#                         'quantity':1,
#                     },
#                     #  {
#                     #     'price':'price_1PHkpnFvgrkbd3pbuO9bqe0E',
#                     #     'quantity':1,
#                     # },
#                 ],
                
#                 mode='subscription',
#                 success_url=settings.SITE_URL + '/?success=true&session_id={CHECKOUT_SESSION_ID}',
#                 cancel_url=settings.SITE_URL + '?canceled=true',
#             )
#             print(checkout_session)
            
#             return redirect(checkout_session.url)
#         except :
#             return Response(
#                 {'error':'Something went wrong when creating stripe checkout session'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#########################################################################################
# class StripeCheckoutView(APIView):
#     def post(self, request):
#         try:
#             products = request.data.get('products', [])
#             if not products or not isinstance(products, list):
#                 return Response(
#                     {'error': 'Invalid products list'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             line_items = []
#             for product in products:
#                 if 'price_id' in product and 'quantity' in product:
#                     line_items.append({
#                         'price': product['price_id'],
#                         'quantity': product['quantity'],
#                     })
#                 else:
#                     return Response(
#                         {'error': 'Each product must include a price_id and quantity'},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )

#             checkout_session = stripe.checkout.Session.create(
#                 payment_method_types=['card'],
#                 line_items=line_items,
#                 mode='subscription',
#                 success_url=f"{settings.SITE_URL}/?success=true&session_id={{CHECKOUT_SESSION_ID}}",
#                 cancel_url=f"{settings.SITE_URL}/?canceled=true",
#             )
#             return Response({'url': checkout_session.url})

#         except stripe.error.StripeError as e:
#             logger.error(f"Stripe error: {e.user_message}")
#             return Response(
#                 {'error': f'Stripe error: {e.user_message}'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#         except Exception as e:
#             logger.error(f"Unexpected error: {e}")
#             return Response(
#                 {'error': 'An unexpected error occurred'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        try:
            products = request.data.get('products', [])
            if not products or not isinstance(products, list):
                return Response(
                    {'error': 'Invalid products list'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = request.user  # Ensure the user is authenticated
            if user.is_anonymous:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            line_items = []
            for product in products:
                if 'price_id' in product and 'quantity' in product:
                    line_items.append({
                        'price': product['price_id'],
                        'quantity': product['quantity'],
                    })
                else:
                    return Response(
                        {'error': 'Each product must include a price_id and quantity'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='subscription',
                success_url=f"{settings.SITE_URL}/?success=true&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.SITE_URL}/?canceled=true",
            )

            # Create a CheckoutSessionRecord
            for item in line_items:
                CheckoutSessionRecord.objects.create(
                    user=user,
                    stripe_customer_id='',  # This will be updated later from the webhook
                    stripe_checkout_session_id=checkout_session.id,
                    stripe_price_id=item['price'],
                    stripe_subscription_id='',
                    current_period_start=None,
                    current_period_end=None,
                    has_access=False,
                    is_completed=False
                )

            return Response({'url': checkout_session.url})

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e.user_message}")
            return Response(
                {'error': f'Stripe error: {e.user_message}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return JsonResponse({'error': 'Invalid signature'}, status=400)

        event_type = event['type']

        if event_type == 'checkout.session.completed':
            self.handle_checkout_session_completed(event['data']['object'])
        elif event_type == 'invoice.payment_succeeded':
            self.handle_invoice_payment_succeeded(event['data']['object'])
        elif event_type == 'customer.subscription.updated':
            self.handle_subscription_updated(event['data']['object'])
        elif event_type == 'customer.subscription.deleted':
            self.handle_subscription_deleted(event['data']['object'])

        return JsonResponse({'status': 'success'})

    def handle_checkout_session_completed(self, session):
        logger.info(f"Received checkout.session.completed event: {session}")

        try:
            record = CheckoutSessionRecord.objects.get(stripe_checkout_session_id=session['id'])
            logger.info(f"Found CheckoutSessionRecord for session ID {session['id']}")

            # Retrieve the subscription object to get current_period_start and current_period_end
            subscription = stripe.Subscription.retrieve(session['subscription'])
            logger.info(f"Retrieved subscription: {subscription}")

            record.stripe_customer_id = session.get('customer')
            record.stripe_subscription_id = session.get('subscription')
            if subscription.get('current_period_start') and subscription.get('current_period_end'):
                record.current_period_start = datetime.fromtimestamp(subscription['current_period_start'])
                record.current_period_end = datetime.fromtimestamp(subscription['current_period_end'])
                logger.info(f"Subscription periods updated: start={record.current_period_start}, end={record.current_period_end}")

            record.has_access = True
            record.is_completed = True
            record.save()
            logger.info(f"CheckoutSessionRecord updated successfully")
        except CheckoutSessionRecord.DoesNotExist:
            logger.error(f"CheckoutSessionRecord not found for session ID {session['id']}")
        except Exception as e:
            logger.error(f"An error occurred while updating CheckoutSessionRecord: {e}")

    def handle_invoice_payment_succeeded(self, invoice):
        logger.info(f"Received invoice.payment_succeeded event: {invoice}")

        try:
            subscription_id = invoice['subscription']
            records = CheckoutSessionRecord.objects.filter(stripe_subscription_id=subscription_id)
            for record in records:
                # Update the record with new period dates if available
                if invoice.get('current_period_start') and invoice.get('current_period_end'):
                    record.current_period_start = datetime.fromtimestamp(invoice['current_period_start'])
                    record.current_period_end = datetime.fromtimestamp(invoice['current_period_end'])
                    logger.info(f"Subscription periods updated: start={record.current_period_start}, end={record.current_period_end}")
                record.save()
        except Exception as e:
            logger.error(f"An error occurred while updating records for invoice {invoice['id']}: {e}")

    def handle_subscription_updated(self, subscription):
        logger.info(f"Received customer.subscription.updated event: {subscription}")

        try:
            records = CheckoutSessionRecord.objects.filter(stripe_subscription_id=subscription['id'])
            for record in records:
                # Update the record with new period dates if available
                if subscription.get('current_period_start') and subscription.get('current_period_end'):
                    record.current_period_start = datetime.fromtimestamp(subscription['current_period_start'])
                    record.current_period_end = datetime.fromtimestamp(subscription['current_period_end'])
                    logger.info(f"Subscription periods updated: start={record.current_period_start}, end={record.current_period_end}")
                record.save()
        except Exception as e:
            logger.error(f"An error occurred while updating records for subscription {subscription['id']}: {e}")

    def handle_subscription_deleted(self, subscription):
        logger.info(f"Received customer.subscription.deleted event: {subscription}")

        try:
            records = CheckoutSessionRecord.objects.filter(stripe_subscription_id=subscription['id'])
            for record in records:
                record.has_access = False
                record.save()
        except Exception as e:
            logger.error(f"An error occurred while updating records for subscription {subscription['id']}: {e}")

class SubscriptionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        latest_record = CheckoutSessionRecord.objects.filter(user=user).order_by('-id').first()

        if latest_record:
            has_access = latest_record.has_access
            subscription_status = 'active' if has_access else 'inactive'
        else:
            has_access = False
            subscription_status = 'inactive'

        return Response({
            'subscription_status': subscription_status,
            'has_access': has_access
        })
    