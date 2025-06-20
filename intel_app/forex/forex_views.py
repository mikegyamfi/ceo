from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required

from intel_app.forms import CurrencyTransactionForm
from intel_app.models import WalletTransaction, CurrencyTransaction, AdminInfo

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from intel_app.forms import CurrencyTransactionForm
from intel_app.models import CurrencyTransaction, WalletTransaction


@login_required
def currency_exchange_view(request):
    user = request.user
    minimum_amount = AdminInfo.objects.filter().first().forex_minimum_amount

    if request.method == 'POST':
        form = CurrencyTransactionForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            currency = form.cleaned_data['currency']
            amount_paid = form.cleaned_data['amount_paid']
            qr_code = form.cleaned_data['qr_code_for_payment']
            full_name = form.cleaned_data['recipient_full_name']

            minimum_amount = AdminInfo.objects.filter().first().forex_minimum_amount

            if amount_paid < float(minimum_amount):
                messages.error(request, f"Minimum transaction amount is GHS {minimum_amount}.")
                return redirect('currency-exchange')

            # Select proper rate based on forex status
            rate = currency.personal_rate if user.forex_status == "Personal" else currency.supplier_rate
            amount_to_be_received = round(amount_paid * rate, 2)

            # Check wallet balance
            if user.wallet < amount_paid:
                messages.error(request, "Insufficient wallet balance.")
                return redirect('currency-exchange')

            try:
                with transaction.atomic():
                    # Deduct wallet
                    user.wallet -= amount_paid
                    user.save()

                    # Create transaction
                    CurrencyTransaction.objects.create(
                        currency=currency,
                        user=user,
                        user_assigned=user,
                        recipient_full_name=full_name,
                        current_currency_rate=rate,
                        amount_paid=amount_paid,
                        qr_code_for_payment=qr_code,
                        amount_to_be_received=amount_to_be_received,
                        status="Pending"
                    )

                    # Log wallet transaction
                    WalletTransaction.objects.create(
                        user=user,
                        transaction_type="Debit",
                        transaction_use=f"Currency purchase: {currency.name}",
                        transaction_amount=amount_paid,
                        new_balance=user.wallet
                    )

                    messages.success(
                        request,
                        f"Transaction successful. You will receive {amount_to_be_received} {currency.short_name}."
                    )
                    return redirect('currency_exchange')

            except Exception as e:
                print("Currency transaction error:", e)
                messages.error(request, "An error occurred while processing your transaction.")
                return redirect('currency-exchange')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = CurrencyTransactionForm(user=user)

    return render(request, 'forex/exchange_form.html', {'form': form, 'minimum_amount': minimum_amount})


@login_required
def transaction_history_view(request):
    transactions = CurrencyTransaction.objects.filter(user=request.user).order_by('-transaction_date')
    return render(request, 'forex/transaction_history.html', {'transactions': transactions})
