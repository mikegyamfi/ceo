import secrets
import json
import requests
from datetime import datetime
from decouple import config

ishare_map = {
    2: 50,
    4: 52,
    7: 2000,
    10: 3000,
    12: 4000,
    15: 5000,
    18: 6000,
    22: 7000,
    25: 8000,
    30: 10000,
    45: 15000,
    60: 20000,
    75: 25000,
    90: 30000,
    120: 40000,
    145: 50000,
    285: 100000,
    560: 200000
}


def ref_generator():
    now_time = datetime.now().strftime('%H%M%S')
    secret = secrets.token_hex(9)

    return f"Best{now_time}Plug{secret}GH".upper()


def top_up_ref_generator():
    now_time = datetime.now().strftime('%H%M')
    secret = secrets.token_hex(1)

    return f"TOPUP-{now_time}{secret}".upper()


def send_bundle(receiver, bundle_amount, reference):
    url = "https://testhub.geosams.com/controller/api/send_bundle/"

    payload = json.dumps({
        "phone_number": str(receiver),
        "amount": int(bundle_amount),
        "reference": str(reference),
        "network": "AT"
    })
    headers = {
        'Authorization': config("CONTROLLER_TOKEN"),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return response


def nexus_send_bundle(receiver, bundle_amount, reference):
    url = "https://nexus.nobledatagh.com/api/send_bundle/"
    print(receiver, bundle_amount, reference)

    payload = json.dumps({
        "phone_number": str(receiver),
        "amount": str(bundle_amount),
        "reference": ref_generator()
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': config("TOKEN_NEXUS")
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    return response


def verify_paystack_transaction(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": "Bearer sk_test_d8585b8c1c61a364640e9acbb3bc8046f5fb9acd"
    }

    response = requests.request("GET", url, headers=headers)

    print(response.json())

    return response

