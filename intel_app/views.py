import hashlib
import hmac
import json
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
from decouple import config
from django.contrib.auth.forms import PasswordResetForm
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
import requests
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from openpyxl import Workbook

from . import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import helper, models
from .forms import UploadFileForm
from .models import CustomUser, MTNTransaction, TelecelTransaction, BigTimeTransaction, IShareBundleTransaction, \
    CheckerType, ResultChecker, ResultCheckerTransaction


# Create your views here.
def home(request):
    announcements = models.Announcement.objects.filter(active=True).values("title", "message", "link")

    # Process announcements to remove 'link' if it's empty or None
    processed_announcements = []
    for announcement in announcements:
        if not announcement["link"] or announcement["link"].strip().lower() == "none":
            del announcement["link"]  # Remove the link field if empty or None
        processed_announcements.append(announcement)

    context = {"announcements": processed_announcements}

    if request.user.is_authenticated:
        user = models.CustomUser.objects.get(id=request.user.id)
        context["wallet"] = user.wallet

    if request.user.is_authenticated:
        user = models.CustomUser.objects.get(id=request.user.id)
        context["wallet"] = user.wallet

    print(context)
    return render(request, "layouts/index.html", context)


def services(request):
    return render(request, "layouts/services.html")


def pay_with_wallet(request):
    if request.method == "POST":

        user = models.CustomUser.objects.get(id=request.user.id)
        phone_number = request.POST.get("phone")
        amount = request.POST.get("amount")
        reference = request.POST.get("reference")
        if user.wallet is None:
            return JsonResponse({'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        elif user.wallet <= 0 or user.wallet < float(amount):
            return JsonResponse({'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        print(phone_number)
        print(amount)
        print(reference)
        if user.status == "User":
            bundle = models.IshareBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Agent":
            bundle = models.AgentIshareBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Super Agent":
            bundle = models.SuperAgentIshareBundlePrice.objects.get(price=float(amount)).bundle_volume
        else:
            bundle = models.IshareBundlePrice.objects.get(price=float(amount)).bundle_volume

        print(bundle)
        ishare_channel = models.AdminInfo.objects.filter().first().ishare_source

        if ishare_channel == "Geosams":
            send_bundle_response = helper.send_bundle(phone_number, bundle, reference)
            try:
                data = send_bundle_response.json()
                print(data)
            except:
                return JsonResponse({'status': f'Something went wrong'})

            sms_headers = {
                'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
                'Content-Type': 'application/json'
            }

            sms_url = 'https://webapp.usmsgh.com/api/sms/send'
            if send_bundle_response.status_code == 200:
                if data["code"] == "200":
                    new_transaction = models.IShareBundleTransaction.objects.create(
                        user=request.user,
                        bundle_number=phone_number,
                        offer=f"{bundle}MB",
                        reference=reference,
                        transaction_status="Completed"
                    )
                    new_transaction.save()
                    user.wallet -= float(amount)
                    user.save()
                    receiver_message = f"Your bundle purchase has been completed successfully. {bundle}MB has been credited to you by {request.user.phone}.\nReference: {reference}\n"
                    sms_message = f"Hello @{request.user.username}. Your bundle purchase has been completed successfully. {bundle}MB has been credited to {phone_number}.\nReference: {reference}\nCurrent Wallet Balance: {user.wallet}\nThank you for using BESTPLUG GH.\n\nThe BESTPLUG GH"

                    try:
                        response1 = requests.get(
                            f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to=0{request.user.phone}&from=BESTPLUG&sms={sms_message}")
                        print(response1.text)

                        response2 = requests.get(
                            f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to={phone_number}&from=BESTPLUG&sms={receiver_message}")
                        print(response2.text)
                    except Exception as e:
                        print(e)

                    new_wallet_transaction = models.WalletTransaction.objects.create(
                        user=request.user,
                        transaction_type="Debit",
                        transaction_amount=float(amount),
                        transaction_use="AT",
                        new_balance=user.wallet
                    )
                    new_wallet_transaction.save()

                    return JsonResponse({'status': 'Transaction Completed Successfully', 'icon': 'success'})
                else:
                    new_transaction = models.IShareBundleTransaction.objects.create(
                        user=request.user,
                        bundle_number=phone_number,
                        offer=f"{bundle}MB",
                        reference=reference,
                        transaction_status="Failed"
                    )
                    new_transaction.save()
                    return JsonResponse({'status': 'Something went wrong', 'icon': 'error'})
            else:
                return JsonResponse({'status': f'Something went wrong'})
        elif ishare_channel == "Noble":
            send_bundle_response = helper.nexus_send_bundle(phone_number, bundle, reference)
            try:
                data = send_bundle_response.json()
                print(data)
            except:
                return JsonResponse({'status': f'Something went wrong'})

            if send_bundle_response.status_code == 200:
                if data["code"] == "200":
                    new_transaction = models.IShareBundleTransaction.objects.create(
                        user=request.user,
                        bundle_number=phone_number,
                        offer=f"{bundle}MB",
                        reference=reference,
                        transaction_status="Completed"
                    )
                    new_transaction.save()
                    user.wallet -= float(amount)
                    user.save()
                    receiver_message = f"Your bundle purchase has been completed successfully. {bundle}MB has been credited to you by {request.user.phone}.\nReference: {reference}\n"
                    sms_message = f"Hello @{request.user.username}. Your bundle purchase has been completed successfully. {bundle}MB has been credited to {phone_number}.\nReference: {reference}\nCurrent Wallet Balance: {user.wallet}\nThank you for using BESTPLUG GH.\n\nThe BESTPLUG GH"

                    try:
                        response1 = requests.get(
                            f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to=0{request.user.phone}&from=BESTPLUG&sms={sms_message}")
                        print(response1.text)

                        response2 = requests.get(
                            f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to={phone_number}&from=BESTPLUG&sms={receiver_message}")
                        print(response2.text)
                    except Exception as e:
                        print(e)

                    new_wallet_transaction = models.WalletTransaction.objects.create(
                        user=request.user,
                        transaction_type="Debit",
                        transaction_amount=float(amount),
                        transaction_use="AT",
                        new_balance=user.wallet
                    )
                    new_wallet_transaction.save()

                    return JsonResponse({'status': 'Transaction Completed Successfully', 'icon': 'success'})
                else:
                    new_transaction = models.IShareBundleTransaction.objects.create(
                        user=request.user,
                        bundle_number=phone_number,
                        offer=f"{bundle}MB",
                        reference=reference,
                        transaction_status="Failed"
                    )
                    new_transaction.save()
                    return JsonResponse({'status': 'Something went wrong', 'icon': 'error'})
            else:
                return JsonResponse({'status': f'Something went wrong'})
    return redirect('airtel-tigo')


@login_required(login_url='login')
def airtel_tigo(request):
    user = models.CustomUser.objects.get(id=request.user.id)
    status = user.status
    form = forms.IShareBundleForm(status)
    reference = helper.ref_generator()
    user_email = request.user.email
    if request.method == "POST":
        form = forms.IShareBundleForm(data=request.POST, status=status)
        payment_reference = request.POST.get("reference")
        amount_paid = request.POST.get("amount")
        new_payment = models.Payment.objects.create(
            user=request.user,
            reference=payment_reference,
            amount=amount_paid,
            transaction_date=datetime.now(),
            transaction_status="Completed"
        )
        new_payment.save()
        print("payment saved")
        print("form valid")
        phone_number = request.POST.get("phone")
        offer = request.POST.get("amount")
        print(offer)
        if user.status == "User":
            bundle = models.IshareBundlePrice.objects.get(price=float(offer)).bundle_volume
        elif user.status == "Agent":
            bundle = models.AgentIshareBundlePrice.objects.get(price=float(offer)).bundle_volume
        elif user.status == "Super Agent":
            bundle = models.SuperAgentIshareBundlePrice.objects.get(price=float(offer)).bundle_volume
        new_transaction = models.IShareBundleTransaction.objects.create(
            user=request.user,
            bundle_number=phone_number,
            offer=f"{bundle}MB",
            reference=payment_reference,
            transaction_status="Pending"
        )
        print("created")
        new_transaction.save()

        print("===========================")
        print(phone_number)
        print(bundle)
        send_bundle_response = helper.send_bundle(request.user, phone_number, bundle, payment_reference)
        data = send_bundle_response.json()

        print(data)

        sms_headers = {
            'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
            'Content-Type': 'application/json'
        }

        sms_url = 'https://webapp.usmsgh.com/api/sms/send'

        if send_bundle_response.status_code == 200:
            if data["code"] == "0000":
                transaction_to_be_updated = models.IShareBundleTransaction.objects.get(reference=payment_reference)
                print("got here")
                print(transaction_to_be_updated.transaction_status)
                transaction_to_be_updated.transaction_status = "Completed"
                transaction_to_be_updated.save()
                print(request.user.phone)
                print("***********")
                receiver_message = f"Your bundle purchase has been completed successfully. {bundle}MB has been credited to you by {request.user.phone}.\nReference: {payment_reference}\n"
                sms_message = f"Hello @{request.user.username}. Your bundle purchase has been completed successfully. {bundle}MB has been credited to {phone_number}.\nReference: {payment_reference}\nThank you for using BESTPLUG GH.\n\nThe BESTPLUG GH"

                # num_without_0 = phone_number[1:]
                # print(num_without_0)
                # receiver_body = {
                #     'recipient': f"233{num_without_0}",
                #     'sender_id': 'BESTPLUG',
                #     'message': receiver_message
                # }
                #
                # response = requests.request('POST', url=sms_url, params=receiver_body, headers=sms_headers)
                # print(response.text)
                #
                # sms_body = {
                #     'recipient': f"233{request.user.phone}",
                #     'sender_id': 'BESTPLUG',
                #     'message': sms_message
                # }
                #
                # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)

                # print(response.text)

                return JsonResponse({'status': 'Transaction Completed Successfully', 'icon': 'success'})
            else:
                transaction_to_be_updated = models.IShareBundleTransaction.objects.get(reference=payment_reference)
                transaction_to_be_updated.transaction_status = "Failed"
                new_transaction.save()
                sms_message = f"Hello @{request.user.username}. Something went wrong with your transaction. Contact us for enquiries.\nBundle: {bundle}MB\nPhone Number: {phone_number}.\nReference: {payment_reference}\nThank you for using BESTPLUG GH.\n\nThe BESTPLUG GH"

                sms_body = {
                    'recipient': f"233{request.user.phone}",
                    'sender_id': 'BESTPLUG',
                    'message': sms_message
                }
                # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
                # print(response.text)
                # r_sms_url = f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=UmpEc1JzeFV4cERKTWxUWktqZEs&to={phone_number}&from=BESTPLUG GH&sms={receiver_message}"
                # response = requests.request("GET", url=r_sms_url)
                # print(response.text)
                return JsonResponse({'status': 'Something went wrong', 'icon': 'error'})
        else:
            transaction_to_be_updated = models.IShareBundleTransaction.objects.get(reference=payment_reference)
            transaction_to_be_updated.transaction_status = "Failed"
            new_transaction.save()
            sms_message = f"Hello @{request.user.username}. Something went wrong with your transaction. Contact us for enquiries.\nBundle: {bundle}MB\nPhone Number: {phone_number}.\nReference: {payment_reference}\nThank you for using BESTPLUG GH.\n\nThe BESTPLUG GH"

            sms_body = {
                'recipient': f'233{request.user.phone}',
                'sender_id': 'BESTPLUG',
                'message': sms_message
            }

            # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
            #
            # print(response.text)
            return JsonResponse({'status': 'Something went wrong', 'icon': 'error'})
    user = models.CustomUser.objects.get(id=request.user.id)
    context = {"form": form, "ref": reference, "email": user_email, "wallet": 0 if user.wallet is None else user.wallet}
    return render(request, "layouts/services/at.html", context=context)


def mtn_pay_with_wallet(request):
    if request.method == "POST":
        user = models.CustomUser.objects.get(id=request.user.id)
        phone = user.phone
        phone_number = request.POST.get("phone")
        amount = request.POST.get("amount")
        reference = request.POST.get("reference")
        print(phone_number)
        print(amount)
        print(reference)
        # sms_headers = {
        #     'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
        #     'Content-Type': 'application/json'
        # }
        #
        # sms_url = 'https://webapp.usmsgh.com/api/sms/send'
        # admin = models.AdminInfo.objects.filter().first().phone_number

        if user.wallet is None:
            return JsonResponse({'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        elif user.wallet <= 0 or user.wallet < float(amount):
            return JsonResponse({'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        if user.status == "User":
            bundle = models.MTNBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Agent":
            bundle = models.AgentMTNBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Super Agent":
            bundle = models.SuperAgentMTNBundlePrice.objects.get(price=float(amount)).bundle_volume

        print(bundle)
        sms_message = f"An order has been placed. {bundle}MB for {phone_number}"
        with transaction.atomic():
            new_mtn_transaction = models.MTNTransaction.objects.create(
                user=request.user,
                bundle_number=phone_number,
                offer=f"{bundle}MB",
                reference=reference,
                amount=amount
            )
            new_mtn_transaction.save()
            user.wallet -= float(amount)
            user.save()

            new_wallet_transaction = models.WalletTransaction.objects.create(
                user=request.user,
                transaction_type="Debit",
                transaction_amount=float(amount),
                transaction_use="MTN",
                new_balance=user.wallet
            )
            new_wallet_transaction.save()
        # sms_body = {
        #     'recipient': "233540975553",
        #     'sender_id': 'BESTPLUG',
        #     'message': sms_message
        # }
        # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
        # print(response.text)
        return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
    return redirect('mtn')


def telecel_pay_with_wallet(request):
    if request.method == "POST":
        user = models.CustomUser.objects.get(id=request.user.id)
        phone = user.phone
        phone_number = request.POST.get("phone")
        amount = request.POST.get("amount")
        reference = request.POST.get("reference")
        print(phone_number)
        print(amount)
        print(reference)
        # sms_headers = {
        #     'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
        #     'Content-Type': 'application/json'
        # }
        #
        # sms_url = 'https://webapp.usmsgh.com/api/sms/send'
        # admin = models.AdminInfo.objects.filter().first().phone_number

        if user.wallet is None:
            return JsonResponse({'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        elif user.wallet <= 0 or user.wallet < float(amount):
            return JsonResponse({'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        if user.status == "User":
            bundle = models.TelecelBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Agent":
            bundle = models.AgentTelecelBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Super Agent":
            bundle = models.SuperAgentTelecelBundlePrice.objects.get(price=float(amount)).bundle_volume

        print(bundle)
        sms_message = f"An order has been placed. {bundle}MB for {phone_number}"
        with transaction.atomic():
            new_telecel_transaction = models.TelecelTransaction.objects.create(
                user=request.user,
                bundle_number=phone_number,
                offer=f"{bundle}MB",
                reference=reference,
                amount=float(amount)
            )
            new_telecel_transaction.save()
            user.wallet -= float(amount)
            user.save()

            new_wallet_transaction = models.WalletTransaction.objects.create(
                user=request.user,
                transaction_type="Debit",
                transaction_amount=float(amount),
                transaction_use="Telecel",
                new_balance=user.wallet
            )
            new_wallet_transaction.save()
        # sms_body = {
        #     'recipient': "233540975553",
        #     'sender_id': 'BESTPLUG',
        #     'message': sms_message
        # }
        # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
        # print(response.text)
        return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
    return redirect('telecel')


@login_required(login_url='login')
def big_time_pay_with_wallet(request):
    if request.method == "POST":
        user = models.CustomUser.objects.get(id=request.user.id)
        phone_number = request.POST.get("phone")
        amount = request.POST.get("amount")
        reference = request.POST.get("reference")
        print(phone_number)
        print(amount)
        print(reference)
        if user.wallet is None:
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        elif user.wallet <= 0 or user.wallet < float(amount):
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        if user.status == "User":
            bundle = models.BigTimeBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Agent":
            bundle = models.AgentBigTimeBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Super Agent":
            bundle = models.SuperAgentBigTimeBundlePrice.objects.get(price=float(amount)).bundle_volume
        print(bundle)

        with transaction.atomic():
            new_mtn_transaction = models.BigTimeTransaction.objects.create(
                user=request.user,
                bundle_number=phone_number,
                offer=f"{bundle}MB",
                reference=reference,
                amount=float(amount)
            )
            new_mtn_transaction.save()
            user.wallet -= float(amount)
            user.save()

            new_wallet_transaction = models.WalletTransaction.objects.create(
                user=request.user,
                transaction_type="Debit",
                transaction_amount=float(amount),
                transaction_use="Big Time",
                new_balance=user.wallet
            )
            new_wallet_transaction.save()

        return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
    return redirect('big_time')


@login_required(login_url='login')
def mtn(request):
    user = models.CustomUser.objects.get(id=request.user.id)
    phone = user.phone
    status = user.status
    form = forms.MTNForm(status=status)
    reference = helper.ref_generator()
    user_email = request.user.email
    if request.method == "POST":
        payment_reference = request.POST.get("reference")
        amount_paid = request.POST.get("amount")
        new_payment = models.Payment.objects.create(
            user=request.user,
            reference=payment_reference,
            amount=amount_paid,
            transaction_date=datetime.now(),
            transaction_status="Completed"
        )
        new_payment.save()
        phone_number = request.POST.get("phone")
        offer = request.POST.get("amount")

        if user.status == "User":
            bundle = models.MTNBundlePrice.objects.get(price=float(offer)).bundle_volume
        elif user.status == "Agent":
            bundle = models.AgentMTNBundlePrice.objects.get(price=float(offer)).bundle_volume
        elif user.status == "Super Agent":
            bundle = models.SuperAgentMTNBundlePrice.objects.get(price=float(offer)).bundle_volume

        new_mtn_transaction = models.MTNTransaction.objects.create(
            user=request.user,
            bundle_number=phone_number,
            offer=f"{bundle}MB",
            reference=payment_reference,

        )
        new_mtn_transaction.save()
        sms_headers = {
            'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
            'Content-Type': 'application/json'
        }

        sms_url = 'https://webapp.usmsgh.com/api/sms/send'
        sms_message = f"An order has been placed. {bundle}MB for {phone_number}"

        sms_body = {
            'recipient': "233540975553",
            'sender_id': 'BESTPLUG',
            'message': sms_message
        }
        # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
        # print(response.text)
        return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
    user = models.CustomUser.objects.get(id=request.user.id)
    phone_num = user.phone
    mtn_dict = {}

    if user.status == "Agent":
        mtn_offer = models.AgentMTNBundlePrice.objects.all()
    else:
        mtn_offer = models.MTNBundlePrice.objects.all()
    for offer in mtn_offer:
        mtn_dict[str(offer)] = offer.bundle_volume
    context = {'form': form, 'phone_num': phone_num, 'mtn_dict': json.dumps(mtn_dict),
               "ref": reference, "email": user_email, "wallet": 0 if user.wallet is None else user.wallet}
    return render(request, "layouts/services/mtn.html", context=context)


@login_required(login_url='login')
def telecel(request):
    user = models.CustomUser.objects.get(id=request.user.id)
    phone = user.phone
    status = user.status
    form = forms.TelecelForm(status=status)
    reference = helper.ref_generator()
    user_email = request.user.email
    if request.method == "POST":
        payment_reference = request.POST.get("reference")
        amount_paid = request.POST.get("amount")
        new_payment = models.Payment.objects.create(
            user=request.user,
            reference=payment_reference,
            amount=amount_paid,
            transaction_date=datetime.now(),
            transaction_status="Completed"
        )
        new_payment.save()
        phone_number = request.POST.get("phone")
        offer = request.POST.get("amount")

        if user.status == "User":
            bundle = models.TelecelBundlePrice.objects.get(price=float(offer)).bundle_volume
        elif user.status == "Agent":
            bundle = models.AgentTelecelBundlePrice.objects.get(price=float(offer)).bundle_volume
        elif user.status == "Super Agent":
            bundle = models.SuperAgentTelecelBundlePrice.objects.get(price=float(offer)).bundle_volume

        new_mtn_transaction = models.MTNTransaction.objects.create(
            user=request.user,
            bundle_number=phone_number,
            offer=f"{bundle}MB",
            reference=payment_reference,

        )
        new_mtn_transaction.save()
        sms_headers = {
            'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
            'Content-Type': 'application/json'
        }

        sms_url = 'https://webapp.usmsgh.com/api/sms/send'
        sms_message = f"An order has been placed. {bundle}MB for {phone_number}"

        sms_body = {
            'recipient': "233540975553",
            'sender_id': 'BESTPLUG',
            'message': sms_message
        }
        # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
        # print(response.text)
        return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
    user = models.CustomUser.objects.get(id=request.user.id)
    phone_num = user.phone

    context = {'form': form, 'phone_num': phone_num,
               "ref": reference, "email": user_email, "wallet": 0 if user.wallet is None else user.wallet}
    return render(request, "layouts/services/voda.html", context=context)


@login_required(login_url='login')
def afa_registration(request):
    user = models.CustomUser.objects.get(id=request.user.id)
    reference = helper.ref_generator()
    db_user_id = request.user.id
    price = models.AdminInfo.objects.filter().first().afa_price
    user_email = request.user.email
    print(price)
    if request.method == "POST":
        form = forms.AFARegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration will be done shortly")
    form = forms.AFARegistrationForm()
    context = {'form': form, 'ref': reference, 'price': price, 'id': db_user_id, "email": user_email,
               "wallet": 0 if user.wallet is None else user.wallet}
    return render(request, "layouts/services/afa.html", context=context)


def afa_registration_wallet(request):
    if request.method == "POST":
        user = models.CustomUser.objects.get(id=request.user.id)
        phone_number = request.POST.get("phone")
        amount = request.POST.get("amount")
        reference = request.POST.get("reference")
        name = request.POST.get("name")
        card_number = request.POST.get("card")
        occupation = request.POST.get("occupation")
        date_of_birth = request.POST.get("birth")
        price = models.AdminInfo.objects.filter().first().afa_price

        if user.wallet is None:
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        elif user.wallet <= 0 or user.wallet < float(amount):
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        
        with transaction.atomic():
            new_registration = models.AFARegistration.objects.create(
                user=user,
                reference=reference,
                name=name,
                phone_number=phone_number,
                gh_card_number=card_number,
                occupation=occupation,
                date_of_birth=date_of_birth
            )
            new_registration.save()
            user.wallet -= float(price)
            user.save()

            new_wallet_transaction = models.WalletTransaction.objects.create(
                user=request.user,
                transaction_type="Debit",
                transaction_amount=float(amount),
                transaction_use="AFA",
                new_balance=user.wallet
            )
            new_wallet_transaction.save()
        return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
    return redirect('home')


@login_required(login_url='login')
def big_time(request):
    user = models.CustomUser.objects.get(id=request.user.id)
    status = user.status
    form = forms.BigTimeBundleForm(status)
    reference = helper.ref_generator()
    db_user_id = request.user.id
    user_email = request.user.email

    if request.method == "POST":
        payment_reference = request.POST.get("reference")
        amount_paid = request.POST.get("amount")
        new_payment = models.Payment.objects.create(
            user=request.user,
            reference=payment_reference,
            amount=amount_paid,
            transaction_date=datetime.now(),
            transaction_status="Pending"
        )
        new_payment.save()
        phone_number = request.POST.get("phone")
        offer = request.POST.get("amount")
        if user.status == "User":
            bundle = models.BigTimeBundlePrice.objects.get(price=float(offer)).bundle_volume
        elif user.status == "Agent":
            bundle = models.AgentBigTimeBundlePrice.objects.get(price=float(offer)).bundle_volume
        elif user.status == "Super Agent":
            bundle = models.SuperAgentBigTimeBundlePrice.objects.get(price=float(offer)).bundle_volume
        print(phone_number)
        new_mtn_transaction = models.BigTimeTransaction.objects.create(
            user=request.user,
            bundle_number=phone_number,
            offer=f"{bundle}MB",
            reference=payment_reference,
        )
        new_mtn_transaction.save()
        return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
    user = models.CustomUser.objects.get(id=request.user.id)
    # phone_num = user.phone
    # mtn_dict = {}
    #
    # if user.status == "Agent":
    #     mtn_offer = models.AgentMTNBundlePrice.objects.all()
    # else:
    #     mtn_offer = models.MTNBundlePrice.objects.all()
    # for offer in mtn_offer:
    #     mtn_dict[str(offer)] = offer.bundle_volume
    context = {'form': form,
               "ref": reference, "email": user_email, 'id': db_user_id,
               "wallet": 0 if user.wallet is None else user.wallet}
    return render(request, "layouts/services/big_time.html", context=context)


@login_required(login_url='login')
def history(request):
    user_transactions = models.IShareBundleTransaction.objects.filter(user=request.user).order_by(
        'transaction_date').reverse()
    header = "AirtelTigo Transactions"
    net = "tigo"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/history.html", context=context)


@login_required(login_url='login')
def mtn_history(request):
    user_transactions = models.MTNTransaction.objects.filter(user=request.user).order_by('transaction_date').reverse()
    header = "MTN Transactions"
    net = "mtn"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/history.html", context=context)


@login_required(login_url='login')
def telecel_history(request):
    user_transactions = models.TelecelTransaction.objects.filter(user=request.user).order_by(
        'transaction_date').reverse()
    header = "Telecel Transactions"
    net = "telecel"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/history.html", context=context)


@login_required(login_url='login')
def big_time_history(request):
    user_transactions = models.BigTimeTransaction.objects.filter(user=request.user).order_by(
        'transaction_date').reverse()
    header = "Big Time Transactions"
    net = "bt"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/history.html", context=context)


@login_required(login_url='login')
def afa_history(request):
    user_transactions = models.AFARegistration.objects.filter(user=request.user).order_by('transaction_date').reverse()
    header = "AFA Registrations"
    net = "afa"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/afa_history.html", context=context)


def verify_transaction(request, reference):
    if request.method == "GET":
        response = helper.verify_paystack_transaction(reference)
        data = response.json()
        try:
            status = data["data"]["status"]
            amount = data["data"]["amount"]
            api_reference = data["data"]["reference"]
            date = data["data"]["paid_at"]
            real_amount = float(amount) / 100
            print(status)
            print(real_amount)
            print(api_reference)
            print(reference)
            print(date)
        except:
            status = data["status"]
        return JsonResponse({'status': status})


def change_excel_status(request, status, to_change_to):
    transactions = models.MTNTransaction.objects.filter(
        transaction_status=status) if to_change_to != "Completed" else models.MTNTransaction.objects.filter(
        transaction_status=status).order_by('transaction_date')[:10]
    for txn in transactions:
        txn.transaction_status = to_change_to
        txn.save()
    messages.success(request, f"Status changed from {status} to {to_change_to}")
    return redirect("mtn_admin", status=status)


from django.db.models import FloatField
from django.db.models.functions import Cast, Substr, Length


@login_required(login_url='login')
def admin_mtn_history(request, status):
    if not (request.user.is_staff and request.user.is_superuser):
        messages.error(request, "Access Denied")
        return redirect('mtn_admin', status=status)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # 1. Pull pending txns, ordered by numeric offer
                queryset = (
                    models.MTNTransaction.objects
                    .filter(transaction_status="Pending")
                    .annotate(
                        offer_value=Cast(Substr('offer', 1, Length('offer') - 2), FloatField())
                    )
                    .order_by('-offer_value')
                )

                # 2. Build Excel in memory
                wb = Workbook()
                ws = wb.active
                ws.title = "MTN Transactions"
                ws.append(["RECIPIENT", "DATA (GB)"])  # header row

                # 3. Fill rows, update status to “Processing”
                for txn in queryset:
                    recipient = f"0{txn.bundle_number}"
                    mb = float(txn.offer.replace('MB', ''))
                    gb = round(mb / 1000, 2)

                    ws.append([recipient, gb])
                    txn.transaction_status = "Processing"
                    txn.save()

                # 4. Save workbook to buffer
                buffer = BytesIO()
                wb.save(buffer)
                buffer.seek(0)

            # If we reach here, the atomic block succeeded & committed
            filename = f"MTNTransactions_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Exception as e:
            # Any exception rolls back all .save() calls inside the atomic block
            messages.error(
                request,
                f"Export failed ({e}). No transactions were updated. Please try again."
            )
            return redirect('mtn_admin', status=status)

    # GET: render the admin page
    all_txns = (
        models.MTNTransaction.objects
        .filter(transaction_status=status)
        .order_by('-transaction_date')[:800]
    )
    return render(
        request,
        "layouts/services/mtn_admin.html",
        {'txns': all_txns, 'status': status}
    )


@login_required(login_url='login')
def admin_telecel_history(request):
    if request.user.is_staff and request.user.is_superuser:
        all_txns = models.TelecelTransaction.objects.all().order_by('-transaction_date')[:1000]
        context = {'txns': all_txns}
        return render(request, "layouts/services/voda_admin.html", context=context)


@login_required(login_url='login')
def admin_at_history(request):
    if request.user.is_staff and request.user.is_superuser:
        all_txns = models.IShareBundleTransaction.objects.filter().order_by('-transaction_date')[:1000]
        context = {'txns': all_txns}
        return render(request, "layouts/services/at_admin.html", context=context)


@login_required(login_url='login')
def admin_bt_history(request):
    if request.user.is_staff and request.user.is_superuser:
        all_txns = models.BigTimeTransaction.objects.filter().order_by('-transaction_date')[:1000]
        context = {'txns': all_txns}
        return render(request, "layouts/services/bt_admin.html", context=context)


@login_required(login_url='login')
def admin_afa_history(request):
    if request.user.is_staff and request.user.is_superuser:
        all_txns = models.AFARegistration.objects.filter().order_by('-transaction_date')[:1000]
        context = {'txns': all_txns}
        return render(request, "layouts/services/afa_admin.html", context=context)


@login_required(login_url='login')
def mark_as_sent(request, pk, status):
    if request.user.is_staff and request.user.is_superuser:
        txn = models.MTNTransaction.objects.filter(id=pk).first()
        print(txn)
        if status == "Processing":
            txn.transaction_status = "Processing"
            txn.save()
            messages.success(request, f"Transaction Processed")
            return redirect('mtn_admin')
        elif status == "Cancelled":
            txn.transaction_status = "Cancelled"
            txn.save()
            messages.success(request, f"Transaction Cancelled")
            return redirect('mtn_admin')
        elif status == "Refunded":
            txn.transaction_status = "Refunded"
            txn.save()
            messages.success(request, f"Transaction Refunded")
            return redirect('mtn_admin')
        else:
            txn.transaction_status = "Completed"
            txn.save()
            sms_headers = {
                'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
                'Content-Type': 'application/json'
            }

            sms_url = 'https://webapp.usmsgh.com/api/sms/send'
            sms_message = f"{txn.bundle_number} has been credited with {txn.offer}.\nTransaction Reference: {txn.reference}"

            sms_body = {
                'recipient': f"233{txn.bundle_number}",
                'sender_id': 'BESTPLUG',
                'message': sms_message
            }
            # response1 = requests.get(
            #     f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to=0{txn.user.phone}&from=BESTPLUG&sms={sms_message}")
            # print(response1.text)
            return redirect('mtn_admin')


@login_required(login_url='login')
def telecel_mark_as_sent(request, pk, status):
    if request.user.is_staff and request.user.is_superuser:
        txn = models.TelecelTransaction.objects.filter(id=pk).first()
        print(txn)
        if status == "Processing":
            txn.transaction_status = "Processing"
            txn.save()
            messages.success(request, f"Transaction Processed")
            return redirect('telecel_admin')
        elif status == "Cancelled":
            txn.transaction_status = "Cancelled"
            txn.save()
            messages.success(request, f"Transaction Cancelled")
            return redirect('telecel_admin')
        elif status == "Refunded":
            txn.transaction_status = "Refunded"
            txn.save()
            messages.success(request, f"Transaction Refunded")
            return redirect('telecel_admin')
        else:
            txn.transaction_status = "Completed"
            txn.save()
            sms_headers = {
                'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
                'Content-Type': 'application/json'
            }

            sms_url = 'https://webapp.usmsgh.com/api/sms/send'
            sms_message = f"{txn.bundle_number} has been credited with {txn.offer}.\nTransaction Reference: {txn.reference}"

            sms_body = {
                'recipient': f"233{txn.bundle_number}",
                'sender_id': 'BESTPLUG',
                'message': sms_message
            }
            response1 = requests.get(
                f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to=0{txn.user.phone}&from=BESTPLUG&sms={sms_message}")
            print(response1.text)
            return redirect('telecel_admin')


@login_required(login_url='login')
def at_mark_as_sent(request, pk, status):
    if request.user.is_staff and request.user.is_superuser:
        txn = models.IShareBundleTransaction.objects.filter(id=pk).first()
        print(txn)
        if status == "Processing":
            txn.transaction_status = "Processing"
            txn.save()
            messages.success(request, f"Transaction Processed")
            return redirect('at_admin')
        elif status == "Cancelled":
            txn.transaction_status = "Cancelled"
            txn.save()
            messages.success(request, f"Transaction Cancelled")
            return redirect('at_admin')
        elif status == "Refunded":
            txn.transaction_status = "Refunded"
            txn.save()
            messages.success(request, f"Transaction Refunded")
            return redirect('at_admin')
        else:
            txn.transaction_status = "Completed"
            txn.save()
            sms_headers = {
                'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
                'Content-Type': 'application/json'
            }

            sms_url = 'https://webapp.usmsgh.com/api/sms/send'
            sms_message = f"Your AT transaction has been completed. {txn.bundle_number} has been credited with {txn.offer}.\nTransaction Reference: {txn.reference}"

            sms_body = {
                'recipient': f"233{txn.user.phone}",
                'sender_id': 'BESTPLUG',
                'message': sms_message
            }
            try:
                response1 = requests.get(
                    f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to=0{txn.user.phone}&from=BESTPLUG&sms={sms_message}")
                print(response1.text)
            except:
                messages.success(request, f"Transaction Completed")
                return redirect('at_admin')
            messages.success(request, f"Transaction Completed")
            return redirect('at_admin')


@login_required(login_url='login')
def bt_mark_as_sent(request, pk, status):
    if request.user.is_staff and request.user.is_superuser:
        txn = models.BigTimeTransaction.objects.filter(id=pk).first()
        print(txn)
        if status == "Processing":
            txn.transaction_status = "Processing"
            txn.save()
            messages.success(request, f"Transaction Processed")
            return redirect('bt_admin')
        elif status == "Cancelled":
            txn.transaction_status = "Cancelled"
            txn.save()
            messages.success(request, f"Transaction Cancelled")
            return redirect('bt_admin')
        elif status == "Refunded":
            txn.transaction_status = "Refunded"
            txn.save()
            messages.success(request, f"Transaction Refunded")
            return redirect('bt_admin')
        else:
            txn.transaction_status = "Completed"
            txn.save()
            sms_headers = {
                'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
                'Content-Type': 'application/json'
            }

            sms_url = 'https://webapp.usmsgh.com/api/sms/send'
            sms_message = f"Your AT BIG TIME transaction has been completed. {txn.bundle_number} has been credited with {txn.offer}.\nTransaction Reference: {txn.reference}"

            sms_body = {
                'recipient': f"233{txn.user.phone}",
                'sender_id': 'BESTPLUG',
                'message': sms_message
            }
            try:
                response1 = requests.get(
                    f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to=0{txn.user.phone}&from=BESTPLUG&sms={sms_message}")
                print(response1.text)
            except:
                messages.success(request, f"Transaction Completed")
                return redirect('bt_admin')
            messages.success(request, f"Transaction Completed")
            return redirect('bt_admin')


@login_required(login_url='login')
def afa_mark_as_sent(request, pk, status):
    if request.user.is_staff and request.user.is_superuser:
        txn = models.AFARegistration.objects.filter(id=pk).first()
        print(txn)
        if status == "Processing":
            txn.transaction_status = "Processing"
            txn.save()
            messages.success(request, f"Transaction Processed")
            return redirect('afa_admin')
        elif status == "Cancelled":
            txn.transaction_status = "Cancelled"
            txn.save()
            messages.success(request, f"Transaction Cancelled")
            return redirect('afa_admin')
        elif status == "Refunded":
            txn.transaction_status = "Refunded"
            txn.save()
            messages.success(request, f"Transaction Refunded")
            return redirect('afa_admin')
        elif status == "Under Verification":
            txn.transaction_status = "Under Verification"
            txn.save()
            messages.success(request, f"Transaction Under Verification")
            return redirect('afa_admin')
        else:
            txn.transaction_status = "Completed"
            txn.save()
            sms_headers = {
                'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
                'Content-Type': 'application/json'
            }

            sms_url = 'https://webapp.usmsgh.com/api/sms/send'
            sms_message = f"Your AFA Registration has been completed. {txn.phone_number} has been registered.\nTransaction Reference: {txn.reference}"

            sms_body = {
                'recipient': f"233{txn.user.phone}",
                'sender_id': 'BESTPLUG',
                'message': sms_message
            }
            response1 = requests.get(
                f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to=0{txn.user.phone}&from=BESTPLUG&sms={sms_message}")
            print(response1.text)
            messages.success(request, f"Transaction Completed")
            return redirect('afa_admin')


@login_required(login_url='login')
def wallet_history(request):
    user_wallet_transactions = models.WalletTransaction.objects.filter(user=request.user).order_by(
        'transaction_date').reverse()[:1000]
    header = "Wallet Transactions"
    net = "wallet"
    wallet = request.user.wallet
    context = {'txns': user_wallet_transactions, "header": header, "net": net, 'wallet': wallet}
    return render(request, "layouts/wallet_history.html", context=context)


def credit_user(request):
    # Only allow superusers to access the view.
    if not request.user.is_superuser:
        messages.error(request, "Access Denied")
        return redirect('home')

    # Instantiate an empty form if not a POST request.
    form = forms.CreditUserForm()

    if request.method == "POST":
        form = forms.CreditUserForm(request.POST)
        if form.is_valid():
            # Get cleaned form data.
            username = form.cleaned_data["user"]
            amount = float(form.cleaned_data["amount"])

            try:
                # Wrap all DB operations in an atomic transaction.
                with transaction.atomic():
                    # Retrieve the user instance.
                    user_needed = models.CustomUser.objects.get(username=username)

                    # If wallet is not set, initialize it with the amount,
                    # otherwise add the amount to the wallet.
                    if user_needed.wallet is None:
                        user_needed.wallet = amount
                    else:
                        user_needed.wallet += amount

                    # Save the updated wallet balance.
                    user_needed.save()

                    # Create a new wallet transaction.
                    new_wallet_transaction = models.WalletTransaction.objects.create(
                        user=user_needed,
                        transaction_type="Credit",
                        transaction_amount=amount,
                        transaction_use="Top up"
                    )
                    # Update the transaction record with the new balance.
                    new_wallet_transaction.new_balance = user_needed.wallet
                    new_wallet_transaction.save()

                # Send SMS notification after successful transaction.
                sms_headers = {
                    'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
                    'Content-Type': 'application/json'
                }
                sms_url = 'https://webapp.usmsgh.com/api/sms/send'
                sms_message = f"Hello {user_needed},\nYour DataForAll wallet has been credited with GHS{amount}.\nDataForAll."
                sms_body = {
                    'recipient': f"233{user_needed.phone}",
                    'sender_id': 'BESTPLUG',
                    'message': sms_message
                }

                response = requests.post(url=sms_url, params=sms_body, headers=sms_headers)
                print(response.text)
                messages.success(request, "Crediting Successful")
                return redirect('credit_user')

            except models.CustomUser.DoesNotExist:
                messages.error(request, "User does not exist")
            except Exception as e:
                # Log the error if needed.
                messages.error(request, f"An error occurred: {e}")

    # Render the form for GET requests or if POST validation fails.
    context = {'form': form}
    return render(request, "layouts/services/credit.html", context=context)


@login_required(login_url='login')
def topup_info(request):
    paystack_active = models.AdminInfo.objects.filter().first().paystack_active
    if request.method == "POST":
        admin = models.AdminInfo.objects.filter().first().phone_number
        user = models.CustomUser.objects.get(id=request.user.id)
        amount = request.POST.get("amount")
        print(amount)
        reference = helper.top_up_ref_generator()
        new_topup_request = models.TopUpRequest.objects.create(
            user=request.user,
            amount=amount,
            reference=reference,
        )
        new_topup_request.save()
        if not models.AdminInfo.objects.filter().first().paystack_active:
            sms_headers = {
                'Authorization': 'Bearer 1136|LwSl79qyzTZ9kbcf9SpGGl1ThsY0Ujf7tcMxvPze',
                'Content-Type': 'application/json'
            }

            sms_url = 'https://webapp.usmsgh.com/api/sms/send'
            sms_message = f"A top up request has been placed.\nGHS{amount} for {user}.\nReference: {reference}"

            sms_body = {
                'recipient': f"233{admin}",
                'sender_id': 'Geosams',
                'message': sms_message
            }
            # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
            # print(response.text)
            messages.success(request,
                             f"Your Request has been sent successfully. Make payment now")
            return redirect("request_successful", reference)
        else:
            url = "https://api.paystack.co/transaction/initialize"

            fields = {
                'email': user.email,
                'amount': int(int(amount) * 100),
                'reference': new_topup_request.reference,
                'callback_url': "https://www.bestpluggh.com",
                'metadata': {
                    'channel': "topup",
                    'real_amount': int(amount),
                    'db_id': user.id,
                }
            }

            headers = {
                "Authorization": config("PAYSTACK_KEY"),
                "Cache-Control": "no-cache"
            }

            response = requests.post(url, json=fields, headers=headers)

            data = response.json()
            print(data)
            url = data['data']['authorization_url']
            return redirect(url)
    return render(request, "layouts/topup-info.html", context={'paystack_active': paystack_active})


@login_required(login_url='login')
def request_successful(request, reference):
    admin = models.AdminInfo.objects.filter().first()
    context = {
        "name": admin.name,
        "number": f"0{admin.momo_number}",
        "channel": admin.payment_channel,
        "reference": reference
    }
    return render(request, "layouts/services/request_successful.html", context=context)


def topup_list(request):
    if request.user.is_superuser:
        topup_requests = models.TopUpRequest.objects.all().order_by('date').reverse()[:200]
        context = {
            'requests': topup_requests,
        }
        return render(request, "layouts/services/topup_list.html", context=context)
    else:
        messages.error(request, "Access Denied")
        return redirect('home')


@login_required(login_url='login')
def credit_user_from_list(request, reference):
    if request.user.is_superuser:
        crediting = models.TopUpRequest.objects.filter(reference=reference).first()
        user = crediting.user
        custom_user = models.CustomUser.objects.get(username=user.username)
        if crediting.status:
            return redirect('topup_list')
        amount = crediting.amount
        print(user)
        print(user.phone)
        print(amount)

        with transaction.atomic():
            custom_user.wallet += amount
            custom_user.save()
            new_wallet_transaction = models.WalletTransaction.objects.create(
                user=custom_user,
                transaction_type="Credit",
                transaction_amount=float(amount),
                transaction_use="Top up",
                new_balance=custom_user.wallet
            )
            new_wallet_transaction.save()
            crediting.status = True
            crediting.credited_at = datetime.now()
            crediting.save()
        sms_headers = {
            'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
            'Content-Type': 'application/json'
        }

        sms_url = 'https://webapp.usmsgh.com/api/sms/send'
        sms_message = f"Hello,\nYour wallet has been topped up with GHS{amount}.\nReference: {reference}.\nThank you"

        sms_body = {
            'recipient': f"233{custom_user.phone}",
            'sender_id': 'BESTPLUG',
            'message': sms_message
        }
        try:
            response1 = requests.get(
                f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to=0{custom_user.phone}&from=BESTPLUG&sms={sms_message}")
            print(response1.text)
        except:
            pass
        messages.success(request, f"{user} has been credited with {amount}")
        return redirect('topup_list')


def populate_custom_users_from_excel(request):
    # Read the Excel file using pandas
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']

            # Process the uploaded Excel file
            df = pd.read_excel(excel_file)
            counter = 0
            # Iterate through rows to create CustomUser instances
            for index, row in df.iterrows():
                print(counter)
                # Create a CustomUser instance for each row
                custom_user = CustomUser.objects.create(
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    username=str(row['username']),
                    email=row['email'],
                    phone=row['phone'],
                    wallet=float(row['wallet']),
                    status=str(row['status']),
                    password1=row['password1'],
                    password2=row['password2'],
                    is_superuser=row['is_superuser'],
                    is_staff=row['is_staff'],
                    is_active=row['is_active'],
                    password=row['password']
                )

                custom_user.save()

                # group_names = row['groups'].split(',')  # Assuming groups are comma-separated
                # groups = Group.objects.filter(name__in=group_names)
                # custom_user.groups.set(groups)
                #
                # if row['user_permissions']:
                #     permission_ids = [int(pid) for pid in row['user_permissions'].split(',')]
                #     permissions = Permission.objects.filter(id__in=permission_ids)
                #     custom_user.user_permissions.set(permissions)
                print("killed")
                counter = counter + 1
            messages.success(request, 'All done')
    else:
        form = UploadFileForm()
    return render(request, 'layouts/import_users.html', {'form': form})


def delete_custom_users(request):
    CustomUser.objects.all().delete()
    return HttpResponseRedirect('Done')


@csrf_exempt
def hubtel_webhook(request):
    if request.method == 'POST':
        print("hit the webhook")
        try:
            payload = request.body.decode('utf-8')
            print("Hubtel payment Info: ", payload)
            json_payload = json.loads(payload)
            print(json_payload)

            data = json_payload.get('Data')
            print(data)
            reference = data.get('ClientReference')
            print(reference)
            txn_status = data.get('Status')
            txn_description = data.get('Description')
            amount = data.get('Amount')
            print(txn_status, amount)

            if txn_status == 'Success':
                print("success")
                transaction_saved = models.Payment.objects.get(reference=reference, transaction_status="Unfinished")
                transaction_saved.transaction_status = "Paid"
                transaction_saved.payment_description = txn_description
                transaction_saved.amount = amount
                transaction_saved.save()
                transaction_details = "hi"
                transaction_channel = "topup"
                user = transaction_saved.user
                # receiver = collection_saved['number']
                # bundle_volume = collection_saved['data_volume']
                # name = collection_saved['name']
                # email = collection_saved['email']
                # phone_number = collection_saved['buyer']
                # date_and_time = collection_saved['date_and_time']
                # txn_type = collection_saved['type']
                # user_id = collection_saved['uid']
                print(transaction_details, transaction_channel)

                if transaction_channel == "ishare":
                    # offer = transaction_details["offers"]
                    # phone_number = transaction_details["phone_number"]
                    #
                    # if user.status == "User":
                    #     bundle = models.IshareBundlePrice.objects.get(price=float(offer)).bundle_volume
                    # elif user.status == "Agent":
                    #     bundle = models.AgentIshareBundlePrice.objects.get(price=float(offer)).bundle_volume
                    # elif user.status == "Super Agent":
                    #     bundle = models.SuperAgentIshareBundlePrice.objects.get(price=float(offer)).bundle_volume
                    # else:
                    #     bundle = models.IshareBundlePrice.objects.get(price=float(offer)).bundle_volume
                    # new_transaction = models.IShareBundleTransaction.objects.create(
                    #     user=user,
                    #     bundle_number=phone_number,
                    #     offer=f"{bundle}MB",
                    #     reference=reference,
                    #     transaction_status="Pending"
                    # )
                    # print("created")
                    # new_transaction.save()
                    #
                    # print("===========================")
                    # print(phone_number)
                    # print(bundle)
                    # print(user)
                    # print(reference)
                    # send_bundle_response = helper.send_bundle(user, phone_number, bundle, reference)
                    # data = send_bundle_response.json()
                    #
                    # print(data)
                    #
                    # sms_headers = {
                    #     'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
                    #     'Content-Type': 'application/json'
                    # }
                    #
                    # sms_url = 'https://webapp.usmsgh.com/api/sms/send'
                    #
                    # if send_bundle_response.status_code == 200:
                    #     if data["code"] == "0000":
                    #         transaction_to_be_updated = models.IShareBundleTransaction.objects.get(
                    #             reference=reference)
                    #         print("got here")
                    #         print(transaction_to_be_updated.transaction_status)
                    #         transaction_to_be_updated.transaction_status = "Completed"
                    #         transaction_to_be_updated.save()
                    #         print(user.phone)
                    #         print("***********")
                    #         receiver_message = f"Your bundle purchase has been completed successfully. {bundle}MB has been credited to you by {user.phone}.\nReference: {reference}\n"
                    #         sms_message = f"Hello @{user.username}. Your bundle purchase has been completed successfully. {bundle}MB has been credited to {phone_number}.\nReference: {reference}\nThank you for using Data4All GH.\n\nThe Data4All GH"
                    #
                    #         sms_body = {
                    #             'recipient': f"233{user.phone}",
                    #             'sender_id': 'BESTPLUG',
                    #             'message': sms_message
                    #         }
                    #         try:
                    #             response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
                    #             print(response.text)
                    #         except:
                    #             print("message not sent")
                    #             pass
                    #         return JsonResponse({'status': 'Transaction Completed Successfully'}, status=200)
                    #     else:
                    #         transaction_to_be_updated = models.IShareBundleTransaction.objects.get(
                    #             reference=reference)
                    #         transaction_to_be_updated.transaction_status = "Failed"
                    #         new_transaction.save()
                    #         sms_message = f"Hello @{user.username}. Something went wrong with your transaction. Contact us for enquiries.\nBundle: {bundle}MB\nPhone Number: {phone_number}.\nReference: {reference}\nThank you for using Data4All GH.\n\nThe Data4All GH"
                    #
                    #         sms_body = {
                    #             'recipient': f"233{user.phone}",
                    #             'sender_id': 'Data4All',
                    #             'message': sms_message
                    #         }
                    #         return JsonResponse({'status': 'Something went wrong'}, status=500)
                    # else:
                    #     transaction_to_be_updated = models.IShareBundleTransaction.objects.get(
                    #         reference=reference)
                    #     transaction_to_be_updated.transaction_status = "Failed"
                    #     new_transaction.save()
                    #     sms_message = f"Hello @{user.username}. Something went wrong with your transaction. Contact us for enquiries.\nBundle: {bundle}MB\nPhone Number: {phone_number}.\nReference: {payment_reference}\nThank you for using Data4All GH.\n\nThe Data4All GH"
                    #
                    #     sms_body = {
                    #         'recipient': f'233{user.phone}',
                    #         'sender_id': 'Data4All',
                    #         'message': sms_message
                    #     }
                    #
                    #     # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
                    #     #
                    #     # print(response.text)
                    #     return JsonResponse({'status': 'Something went wrong', 'icon': 'error'})
                    ...
                elif transaction_channel == "mtn":
                    # offer = transaction_details["offers"]
                    # phone_number = transaction_details["phone_number"]
                    #
                    # if user.status == "User":
                    #     bundle = models.MTNBundlePrice.objects.get(price=float(offer)).bundle_volume
                    # elif user.status == "Agent":
                    #     bundle = models.AgentMTNBundlePrice.objects.get(price=float(offer)).bundle_volume
                    # elif user.status == "Super Agent":
                    #     bundle = models.SuperAgentMTNBundlePrice.objects.get(price=float(offer)).bundle_volume
                    # else:
                    #     bundle = models.MTNBundlePrice.objects.get(price=float(offer)).bundle_volume
                    #
                    # print(phone_number)
                    # new_mtn_transaction = models.MTNTransaction.objects.create(
                    #     user=user,
                    #     bundle_number=phone_number,
                    #     offer=f"{bundle}MB",
                    #     reference=reference,
                    # )
                    # new_mtn_transaction.save()
                    # return JsonResponse({'status': "Your transaction will be completed shortly"}, status=200)
                    ...
                elif transaction_channel == "bigtime":
                    # offer = transaction_details["offers"]
                    # phone_number = transaction_details["phone_number"]
                    # if user.status == "User":
                    #     bundle = models.BigTimeBundlePrice.objects.get(price=float(offer)).bundle_volume
                    # elif user.status == "Agent":
                    #     bundle = models.AgentBigTimeBundlePrice.objects.get(price=float(offer)).bundle_volume
                    # elif user.status == "Super Agent":
                    #     bundle = models.SuperAgentBigTimeBundlePrice.objects.get(price=float(offer)).bundle_volume
                    # else:
                    #     bundle = models.SuperAgentBigTimeBundlePrice.objects.get(price=float(offer)).bundle_volume
                    # print(phone_number)
                    # new_mtn_transaction = models.BigTimeTransaction.objects.create(
                    #     user=user,
                    #     bundle_number=phone_number,
                    #     offer=f"{bundle}MB",
                    #     reference=reference,
                    # )
                    # new_mtn_transaction.save()
                    # return JsonResponse({'status': "Your transaction will be completed shortly"}, status=200)
                    ...
                elif transaction_channel == "afa":
                    # name = transaction_details["name"]
                    # phone_number = transaction_details["phone"]
                    # gh_card_number = transaction_details["card"]
                    # occupation = transaction_details["occupation"]
                    # date_of_birth = transaction_details["date_of_birth"]
                    #
                    # new_afa_reg = models.AFARegistration.objects.create(
                    #     user=user,
                    #     phone_number=phone_number,
                    #     gh_card_number=gh_card_number,
                    #     name=name,
                    #     occupation=occupation,
                    #     reference=reference,
                    #     date_of_birth=date_of_birth
                    # )
                    # new_afa_reg.save()
                    # return JsonResponse({'status': "Your transaction will be completed shortly"}, status=200)
                    ...
                elif transaction_channel == "topup":
                    amount = amount

                    user.wallet += float(amount)
                    user.save()

                    new_topup = models.TopUpRequest.objects.create(
                        user=user,
                        reference=reference,
                        amount=amount,
                        status=True,
                    )
                    new_topup.save()
                    response1 = requests.get(
                        f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to=0{user.phone}&from=BESTPLUG&sms=Your Bestplug wallet has been credited with {amount}. Thank You.")
                    print(response1.text)
                    return JsonResponse({'status': "Wallet Credited"}, status=200)
                else:
                    print("no type found")
                    return JsonResponse({'message': "No Type Found"}, status=500)
            else:
                print("Transaction was not Successful")
                return JsonResponse({'message': 'Transaction Failed'}, status=200)
        except Exception as e:
            print("Error Processing hubtel webhook:", str(e))
            return JsonResponse({'status': 'error'}, status=500)
    else:
        print("not post")
        return JsonResponse({'message': 'Not Found'}, status=404)


@csrf_exempt
def paystack_webhook(request):
    if request.method == "POST":
        paystack_secret_key = config("PAYSTACK_SECRET_KEY")
        # print(paystack_secret_key)
        payload = json.loads(request.body)

        paystack_signature = request.headers.get("X-Paystack-Signature")

        if not paystack_secret_key or not paystack_signature:
            return HttpResponse(status=400)

        computed_signature = hmac.new(
            paystack_secret_key.encode('utf-8'),
            request.body,
            hashlib.sha512
        ).hexdigest()

        if computed_signature == paystack_signature:
            print("yes")
            print(payload.get('data'))
            r_data = payload.get('data')
            print(r_data.get('metadata'))
            print(payload.get('event'))
            if payload.get('event') == 'charge.success':

                try:
                    metadata = r_data.get('metadata')
                    receiver = metadata.get('receiver')
                    db_id = metadata.get('db_id')
                    print(db_id)
                    # offer = metadata.get('offer')
                    user = models.CustomUser.objects.get(id=int(db_id))
                    print(user)
                    channel = metadata.get('channel')
                    real_amount = metadata.get('real_amount')
                    print(real_amount)
                    paid_amount = r_data.get('amount')
                    reference = r_data.get('reference')

                    paid_amount = r_data.get('amount')
                    reference = r_data.get('reference')

                    slashed_amount = float(paid_amount) / 100
                    reference = r_data.get('reference')

                    if channel == "ishare":
                        if user.status == "User":
                            bundle = models.IshareBundlePrice.objects.get(price=float(real_amount)).bundle_volume
                        elif user.status == "Agent":
                            bundle = models.AgentIshareBundlePrice.objects.get(price=float(real_amount)).bundle_volume
                        elif user.status == "Super Agent":
                            bundle = models.SuperAgentIshareBundlePrice.objects.get(price=float(real_amount)).bundle_volume
                        else:
                            bundle = models.IshareBundlePrice.objects.get(price=float(real_amount)).bundle_volume

                        if models.IShareBundleTransaction.objects.filter(reference=reference, offer=f"{bundle}MB",
                                                                         transaction_status="Completed").exists():
                            return HttpResponse(status=200)


                        else:
                            send_bundle_response = helper.send_bundle(receiver, bundle, reference)
                            try:
                                data = send_bundle_response.json()
                                print(data)
                            except:
                                return HttpResponse(status=500)

                            sms_headers = {
                                'Authorization': 'Bearer 1334|wroIm5YnQD6hlZzd8POtLDXxl4vQodCZNorATYGX',
                                'Content-Type': 'application/json'
                            }

                            sms_url = 'https://webapp.usmsgh.com/api/sms/send'
                            if send_bundle_response.status_code == 200:
                                if data["status"] == "Success":
                                    new_transaction = models.IShareBundleTransaction.objects.create(
                                        user=user,
                                        bundle_number=receiver,
                                        offer=f"{bundle}MB",
                                        reference=reference,
                                        transaction_status="Completed"
                                    )
                                    new_transaction.save()
                                    receiver_message = f"Your bundle purchase has been completed successfully. {bundle}MB has been credited to you by {user.phone}.\nReference: {reference}\n"
                                    sms_message = f"Hello @{request.user.username}. Your bundle purchase has been completed successfully. {bundle}MB has been credited to {receiver}.\nReference: {reference}\nCurrent Wallet Balance: {user.wallet}\nThank you for using GH BAY."

                                    num_without_0 = receiver[1:]
                                    print(num_without_0)
                                    receiver_body = {
                                        'recipient': f"233{num_without_0}",
                                        'sender_id': 'GH BAY',
                                        'message': receiver_message
                                    }

                                    response = requests.request('POST', url=sms_url, params=receiver_body,
                                                                headers=sms_headers)
                                    print(response.text)

                                    sms_body = {
                                        'recipient': f"233{request.user.phone}",
                                        'sender_id': 'GH BAY',
                                        'message': sms_message
                                    }

                                    response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)

                                    print(response.text)
                                    return HttpResponse(status=200)
                                else:
                                    new_transaction = models.IShareBundleTransaction.objects.create(
                                        user=user,
                                        bundle_number=receiver,
                                        offer=f"{bundle}MB",
                                        reference=reference,
                                        transaction_status="Pending"
                                    )
                                    new_transaction.save()
                                    return HttpResponse(status=500)
                            else:
                                new_transaction = models.IShareBundleTransaction.objects.create(
                                    user=user,
                                    bundle_number=receiver,
                                    offer=f"{bundle}MB",
                                    reference=reference,
                                    transaction_status="Pending"
                                )
                                new_transaction.save()
                                return HttpResponse(status=500)
                    elif channel == "mtn":
                        new_payment = models.Payment.objects.create(
                            user=user,
                            reference=reference,
                            amount=paid_amount,
                            transaction_date=datetime.now(),
                            transaction_status="Pending"
                        )
                        new_payment.save()

                        if user.status == "User":
                            bundle = models.MTNBundlePrice.objects.get(price=float(real_amount)).bundle_volume
                        elif user.status == "Agent":
                            bundle = models.AgentMTNBundlePrice.objects.get(price=float(real_amount)).bundle_volume
                        elif user.status == "Super Agent":
                            bundle = models.SuperAgentMTNBundlePrice.objects.get(price=float(real_amount)).bundle_volume
                        else:
                            bundle = models.MTNBundlePrice.objects.get(price=float(real_amount)).bundle_volume

                        print(receiver)

                        new_mtn_transaction = models.MTNTransaction.objects.create(
                            user=user,
                            bundle_number=receiver,
                            offer=f"{bundle}MB",
                            reference=reference,
                        )
                        new_mtn_transaction.save()
                        return HttpResponse(status=200)
                    elif channel == "at_min":
                        new_payment = models.Payment.objects.create(
                            user=user,
                            reference=reference,
                            amount=paid_amount,
                            transaction_date=datetime.now(),
                            transaction_status="Pending"
                        )
                        new_payment.save()

                        if user.status == "User":
                            minutes = models.ATCreditPrice.objects.get(price=float(real_amount)).minutes
                        else:
                            minutes = models.ATCreditPrice.objects.get(price=float(real_amount)).minutes

                        print(receiver)

                        new_mtn_transaction = models.ATMinuteTransaction.objects.create(
                            user=user,
                            bundle_number=receiver,
                            offer=f"{minutes} Minutes",
                            reference=reference,
                        )
                        new_mtn_transaction.save()
                        return HttpResponse(status=200)
                    elif channel == "afa_credit":
                        new_payment = models.Payment.objects.create(
                            user=user,
                            reference=reference,
                            amount=paid_amount,
                            transaction_date=datetime.now(),
                            transaction_status="Pending"
                        )
                        new_payment.save()

                        if user.status == "User":
                            minutes = models.AfaCreditPrice.objects.get(price=float(real_amount)).minutes
                        else:
                            minutes = models.AfaCreditPrice.objects.get(price=float(real_amount)).minutes

                        print(receiver)

                        new_mtn_transaction = models.AfaCreditTransaction.objects.create(
                            user=user,
                            bundle_number=receiver,
                            offer=f"{minutes} Minutes",
                            reference=reference,
                        )
                        new_mtn_transaction.save()
                        return HttpResponse(status=200)
                    elif channel == "big-time":
                        new_payment = models.Payment.objects.create(
                            user=user,
                            reference=reference,
                            amount=paid_amount,
                            transaction_date=datetime.now(),
                            transaction_status="Pending"
                        )
                        new_payment.save()

                        if user.status == "User":
                            bundle = models.BigTimeBundlePrice.objects.get(price=float(real_amount)).bundle_volume
                        elif user.status == "Agent":
                            bundle = models.AgentBigTimeBundlePrice.objects.get(price=float(real_amount)).bundle_volume
                        elif user.status == "Super Agent":
                            bundle = models.SuperAgentBigTimeBundlePrice.objects.get(price=float(real_amount)).bundle_volume
                        else:
                            bundle = models.BigTimeBundlePrice.objects.get(price=float(real_amount)).bundle_volume

                        print(receiver)

                        new_transaction = models.BigTimeTransaction.objects.create(
                            user=user,
                            bundle_number=receiver,
                            offer=f"{bundle}MB",
                            reference=reference,
                        )
                        new_transaction.save()
                        return HttpResponse(status=200)
                    elif channel == "afa":
                        phone_number = metadata.get('phone_number')
                        gh_card_number = metadata.get('card_number')
                        name = metadata.get('name')
                        occupation = metadata.get('occupation')
                        date_of_birth = metadata.get('dob')

                        new_payment = models.Payment.objects.create(
                            user=user,
                            reference=reference,
                            amount=paid_amount,
                            transaction_date=datetime.now(),
                            transaction_status="Pending"
                        )
                        new_payment.save()

                        new_afa_txn = models.AFARegistration2.objects.create(
                            user=user,
                            reference=reference,
                            name=name,
                            gh_card_number=gh_card_number,
                            phone_number=phone_number,
                            occupation=occupation,
                            date_of_birth=date_of_birth
                        )
                        new_afa_txn.save()
                        return HttpResponse(status=200)
                    elif channel == "topup":
                        if models.TopUpRequest.objects.filter(reference=reference, status=True).exists():
                            return HttpResponse(status=200)
                        try:
                            amount = real_amount
                            with transaction.atomic():
                                user.wallet += float(amount)
                                user.save()

                                topup_request = models.TopUpRequest.objects.get(reference=reference)
                                topup_request.status = True
                                topup_request.save()

                                new_wallet_transaction = models.WalletTransaction.objects.create(
                                    user=user,
                                    transaction_type="Credit",
                                    transaction_amount=float(amount),
                                    transaction_use=f"Top up (Paystack) ({reference})",
                                    new_balance=user.wallet
                                )
                                new_wallet_transaction.save()
                            return HttpResponse(status=200)
                        except Exception as e:
                            print(e)
                            return HttpResponse(status=200)
                    elif channel == "commerce":
                        phone_number = metadata.get('phone_number')
                        region = metadata.get('region')
                        name = metadata.get('name')
                        city = metadata.get('city')
                        message = metadata.get('message')
                        address = metadata.get('address')
                        order_mail = metadata.get('order_mail')

                        print(phone_number, region, name, city, message, address, order_mail)

                        new_order_items = models.Cart.objects.filter(user=user)
                        cart = models.Cart.objects.filter(user=user)
                        cart_total_price = 0
                        for item in cart:
                            cart_total_price += item.product.selling_price * item.product_qty
                        print(cart_total_price)
                        print(user.wallet)
                        if models.Order.objects.filter(tracking_number=reference, message=message,
                                                       payment_id=reference).exists():
                            return HttpResponse(status=200)
                        with transaction.atomic():
                            order_form = models.Order.objects.create(
                                user=user,
                                full_name=name,
                                email=order_mail,
                                phone=phone_number,
                                address=address,
                                city=city,
                                region=region,
                                total_price=cart_total_price,
                                payment_mode="Paystack",
                                payment_id=reference,
                                message=message,
                                tracking_number=reference
                            )
                            order_form.save()

                            for item in new_order_items:
                                models.OrderItem.objects.create(
                                    order=order_form,
                                    product=item.product,
                                    tracking_number=order_form.tracking_number,
                                    price=item.product.selling_price,
                                    quantity=item.product_qty
                                )
                                order_product = models.Product.objects.filter(id=item.product_id).first()
                                order_product.quantity -= item.product_qty
                                order_product.save()

                            models.Cart.objects.filter(user=user).delete()

                        sms_headers = {
                            'Authorization': 'Bearer 1334|wroIm5YnQD6hlZzd8POtLDXxl4vQodCZNorATYGX',
                            'Content-Type': 'application/json'
                        }

                        sms_url = 'https://webapp.usmsgh.com/api/sms/send'
                        sms_message = f"Order Placed Successfully\nYour order with order number {order_form.tracking_number} has been received and is being processed.\nYou will receive a message when your order is Out for Delivery.\nThank you for shopping with GH BAY"

                        sms_body = {
                            'recipient': f"233{order_form.phone}",
                            'sender_id': 'GH BAY',
                            'message': sms_message
                        }
                        try:
                            response1 = requests.get(
                                f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A=&to=0{order_form.phone}&from=BESTPLUG&sms={sms_message}")
                            print(response1.text)
                        except:
                            print("Could not send sms message")
                        return HttpResponse(status=200)
                    elif channel == "voda":
                        return HttpResponse(status=200)
                    elif channel == "checker":
                        """
                        1. Retrieve the checker info from metadata
                        2. Allocate pins
                        3. Mark them used and create transactions
                        4. Send SMS if desired
                        """
                        checker_type_name = metadata.get('checker_type_name')
                        quantity = int(metadata.get('quantity', 1))

                        # Fetch the CheckerType by name
                        try:
                            checker_type = CheckerType.objects.get(name=checker_type_name)
                        except CheckerType.DoesNotExist:
                            print("Checker type not found")
                            return HttpResponse(status=200)

                        # Get enough unused pins for this checker_type
                        available_pins = ResultChecker.objects.filter(
                            checker_type=checker_type,
                            used=False
                        )[:quantity]

                        # If not enough pins, do something
                        if len(available_pins) < quantity:
                            print("Not enough pins to fulfill the order.")
                            return HttpResponse(status=200)

                        # Mark pins as used, create transactions, optionally send SMS
                        for pin_item in available_pins:
                            pin_item.used = True
                            pin_item.save()

                            # Create a transaction
                            ResultCheckerTransaction.objects.create(
                                user=user,
                                result_checker=pin_item,
                                amount=slashed_amount
                            )

                            # Send an SMS with the PIN and Serial, if you want
                            # Example pseudo-SMS code:
                            try:
                                sms_headers = {
                                    'Authorization': 'Bearer 1140|qFllpsDETDvxvpIUM74uQSVS2Iin3oVoi0SgzPyd',
                                    'Content-Type': 'application/json'
                                }
                                sms_url = 'https://webapp.usmsgh.com/api/sms/send'
                                sms_message = f"Hello {user.username},\n" \
                                              f"Here is your {checker_type_name} checker:\n" \
                                              f"PIN: {pin_item.pin}\n" \
                                              f"Serial: {pin_item.serial_number}\n" \
                                              f"Ref: {reference}\n" \
                                              f"Thank you for using GH BAY."

                                # user.phone or receiver or whichever phone number you want
                                final_phone_number = f"233{user.phone[1:]}" if user.phone.startswith('0') else user.phone

                                sms_body = {
                                    'recipient': final_phone_number,
                                    'sender_id': 'BESTPLUG',
                                    'message': sms_message
                                }
                                response = requests.post(sms_url, params=sms_body, headers=sms_headers)
                                print(response.text)
                            except Exception as e:
                                print("Could not send checker SMS: ", e)
                        return HttpResponse(status=200)
                    else:
                        return HttpResponse(status=200)
                except Exception as e:
                    print(e)
                    return HttpResponse(status=200)
            else:
                return HttpResponse(status=200)
        else:
            return HttpResponse(status=401)


def cancel_mtn_transaction(request, pk, net):
    print(net)
    user = models.CustomUser.objects.get(id=request.user.id)
    if net == "mtn":
        print("mtn selected")
        try:
            transaction_to_be_canceled = models.MTNTransaction.objects.get(id=pk, user=user, transaction_status="Pending")
        except Exception as e:
            print(e)
            messages.info(request, "Could not cancel transaction")
            return redirect('mtn-history')
    elif net == "bt":
        print("big time selected")
        try:
            transaction_to_be_canceled = models.BigTimeTransaction.objects.get(id=pk, user=user,
                                                                               transaction_status="Pending")
        except Exception as e:
            print(e)
            messages.info(request, "Could not cancel transaction")
            return redirect('bt-history')
    elif net == "telecel":
        print("telecel selected")
        try:
            transaction_to_be_canceled = models.TelecelTransaction.objects.get(id=pk, user=user,
                                                                               transaction_status="Pending")
        except Exception as e:
            print(e)
            messages.info(request, "Could not cancel transaction")
            return redirect('telecel-history')
    else:
        return redirect('history')


    try:
        with transaction.atomic():
            amount_to_refund = transaction_to_be_canceled.amount
            transaction_to_be_canceled.transaction_status = 'Canceled'
            transaction_to_be_canceled.save()
            user.wallet += float(amount_to_refund)
            user.save()

            if net == "mtn":
                new_wallet_transaction = models.WalletTransaction.objects.create(
                    user=user,
                    transaction_type="Credit",
                    transaction_amount=float(amount_to_refund),
                    transaction_use="Refund(MTN)",
                    new_balance=user.wallet
                )
                new_wallet_transaction.save()
            elif net == "bt":
                new_wallet_transaction = models.WalletTransaction.objects.create(
                    user=user,
                    transaction_type="Credit",
                    transaction_amount=float(amount_to_refund),
                    transaction_use="Refund(BigTime)",
                    new_balance=user.wallet
                )
                new_wallet_transaction.save()
            elif net == "telecel":
                new_wallet_transaction = models.WalletTransaction.objects.create(
                    user=user,
                    transaction_type="Credit",
                    transaction_amount=float(amount_to_refund),
                    transaction_use="Refund(Telecel)",
                    new_balance=user.wallet
                )
                new_wallet_transaction.save()
    except Exception as e:
        print(e)
        messages.info(request, "Unable to cancel transaction")
        return redirect('mtn-history')

    transaction_to_be_canceled.delete()

    messages.success(request, "Transaction has been cancelled and money refunded into wallet")

    return redirect('mtn-history')


from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            user = models.CustomUser.objects.filter(email=data).first()
            current_user = user
            if user:
                subject = "Password Reset Requested"
                email_template_name = "password/password_reset_message.txt"
                c = {
                    "name": user.first_name,
                    "email": user.email,
                    'domain': 'www.bestpluggh.com',
                    'site_name': 'Best Plug GH',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https',
                }
                email = render_to_string(email_template_name, c)
                print(email)

                response1 = requests.get(
                    f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=OnBuSjBXc1pqN0xrQXIxU1A&to=0{user.phone}&from=BESTPLUG&sms={email}")
                print(response1.text)

                return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html",
                  context={"password_reset_form": password_reset_form})











