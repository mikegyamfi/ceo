# views.py
import secrets
import string

from decouple import config
from django.db import transaction
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
import requests  # If you'll call Paystack or external APIs

from intel_app.models import CheckerType, ResultChecker, ResultCheckerTransaction, CustomUser, WalletTransaction


# 1. Display all checker types
class CheckerTypeListView(View):
    """
    Lists all the available checker types in a card-style layout.
    """

    def get(self, request, *args, **kwargs):
        checker_types = CheckerType.objects.all()
        return render(request, 'checker/checker_types.html', {'checker_types': checker_types})


# 2. Show a form to select how many checkers to buy
class CheckerBuyView(LoginRequiredMixin, View):
    """
    Renders a form with the selected checker type and allows user to input quantity.
    """

    def get(self, request, pk, *args, **kwargs):
        checker_type = get_object_or_404(CheckerType, pk=pk)
        return render(request, 'checker/checker_buy.html', {'checker_type': checker_type})

    def post(self, request, pk, *args, **kwargs):
        """
        User has selected how many checkers they'd like to buy,
        so we store that data in session or pass it directly to the checkout.
        """
        checker_type = get_object_or_404(CheckerType, pk=pk)
        quantity = request.POST.get('quantity')

        if not quantity or int(quantity) < 1:
            messages.error(request, "Please enter a valid quantity.")
            return redirect('buy_checker', pk=pk)

        # Option A: Save in session
        request.session['checker_type_id'] = checker_type.id
        request.session['checker_quantity'] = quantity

        # Redirect to a checkout view/page
        return redirect('checkout_checker')


# 3. Checkout View
class CheckerCheckoutView(LoginRequiredMixin, View):
    """
    Displays a summary of the purchase (checker type, quantity, total price)
    and either shows a Paystack redirect button or wallet payment option, etc.
    """

    def get(self, request, *args, **kwargs):
        checker_type_id = request.session.get('checker_type_id')
        quantity = request.session.get('checker_quantity')

        if not checker_type_id or not quantity:
            messages.error(request, "Something went wrong. Please select your Checker Type and Quantity again.")
            return redirect('checker_types')

        checker_type = get_object_or_404(CheckerType, pk=checker_type_id)
        total_amount = float(checker_type.price) * float(quantity)

        # Generate a reference for Paystack
        reference = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        request.session['checker_reference'] = reference

        context = {
            'checker_type': checker_type,
            'quantity': quantity,
            'total_amount': total_amount,
            'reference': reference,
            'user_email': request.user.email,
            # If you have a wallet system:
            'wallet_balance': getattr(request.user, 'wallet_balance', 0),
        }
        return render(request, 'checker/checker_checkout.html', context)

    def post(self, request, *args, **kwargs):
        checker_type_id = request.session.get('checker_type_id')
        quantity = int(request.session.get('checker_quantity', 0))
        reference = request.session.get('checker_reference')
        checker_type = get_object_or_404(CheckerType, pk=checker_type_id)
        total_amount = float(checker_type.price) * quantity
        user = request.user

        if user.wallet < total_amount:
            return JsonResponse({'status': "Insufficient wallet balance!"}, status=400)

        with transaction.atomic():
            user.wallet -= total_amount
            user.save()

            pins = list(
                ResultChecker.objects
                .select_for_update()
                .filter(checker_type=checker_type, used=False)[:quantity]
            )
            if len(pins) < quantity:
                messages.error(request, "Not enough pins available to fulfill your order.")
                # Raising here causes the atomic block to roll back
                raise ValueError("Insufficient pins")

            # 3. For each pin: mark used + record both transactions
            for pin in pins:
                pin.used = True
                pin.save()

                ResultCheckerTransaction.objects.create(
                    user=user,
                    result_checker=pin,
                    amount=checker_type.price
                )

                WalletTransaction.objects.create(
                    user=user,
                    transaction_type="Debit",
                    transaction_amount=checker_type.price,
                    transaction_use="Result Checker Purchase",
                    new_balance=user.wallet
                )

        # If we get here, everything committed cleanly
        messages.success(request, f"Successfully purchased {quantity} pins.")
        return redirect('checker_history')


class VerifyCheckerPaymentView(LoginRequiredMixin, View):
    """
    If your Paystack integration returns you here after successful payment,
    you can verify the payment and then finalize the transaction.
    """

    def get(self, request, *args, **kwargs):
        reference = request.GET.get('reference', None)
        if not reference:
            messages.error(request, "No reference provided.")
            return redirect('checker_types')

        # Verify with Paystack
        verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        resp = requests.get(verify_url, headers=headers)
        data = resp.json()

        if data['status']:
            # Payment successful
            # Retrieve from session
            checker_type_id = request.session.get('checker_type_id')
            quantity = request.session.get('checker_quantity')
            checker_type = get_object_or_404(CheckerType, pk=checker_type_id)
            total_amount = float(checker_type.price) * float(quantity)

            finalize_transaction(request.user, checker_type, quantity, total_amount, reference)
            messages.success(request, "Payment successful! Your pins and serials will be sent shortly.")
            return redirect('checker_history')
        else:
            messages.error(request, "Payment verification failed.")
            return redirect('checker_types')


# 5. The Paystack webhook
from django.views.decorators.csrf import csrf_exempt
import json


# 6. Transaction history
class CheckerHistoryView(LoginRequiredMixin, View):
    """
    Shows the user all checker pins they've purchased.
    """

    def get(self, request, *args, **kwargs):
        transactions = ResultCheckerTransaction.objects.filter(user=request.user).order_by('-date_bought')
        return render(request, 'checker/checker_history.html', {'transactions': transactions})


# Helper function: finalize_transaction
def finalize_transaction(user, checker_type, quantity, total_amount, reference):
    """
    Takes the user, checker type, quantity, total amount, and payment reference,
    picks the correct number of available (unused) pins/serials, sends SMS,
    marks them used, and creates transaction records.
    """
    # 1. Fetch the required number of unused pins for this checker_type
    available_pins = ResultChecker.objects.filter(checker_type=checker_type, used=False)[:int(quantity)]
    if len(available_pins) < int(quantity):
        # Not enough pins
        # handle logic (refund or partial??)
        return

    for pin_item in available_pins:
        # Mark as used
        pin_item.used = True
        pin_item.save()
        # Create a transaction for each pin
        ResultCheckerTransaction.objects.create(
            user=user,
            result_checker=pin_item,
            amount=total_amount,  # or checker_type.price if you want each
        )

        # Send SMS logic
        # e.g., call Twilio or other service
        # pseudo-code:
        # sms_body = f"Your {checker_type.name} pin: {pin_item.pin}, serial: {pin_item.serial_number}"
        # send_sms(to=user.phone_number, body=sms_body)

    # Optionally store an overall purchase record if needed
    # Or rely on the multiple transactions.
