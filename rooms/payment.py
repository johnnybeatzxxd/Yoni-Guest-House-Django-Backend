import requests
import json
import uuid
import os
from dotenv import load_dotenv

load_dotenv()


url = "https://api.chapa.co/v1/transaction/initialize"

def initiate_payment(first_name,last_name,email,phone_number,amount,description,tx_ref):
    chapa_key = os.getenv("CHAPA_API")

    payload = {
        "amount": amount,
        "currency": "ETB",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "tx_ref": tx_ref,  
        "callback_url": "https://yoni-guest-house-django-backend.vercel.app/rooms/pay",
        "return_url": "https://www.yoniguesthouse.top",
        "customization": {
            "title": "Yoni Guest House",
            "description": description
        }
    }

    headers = {
        'Authorization': f'Bearer {chapa_key}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()  
        print(data["data"]["checkout_url"])  
        return data["data"]["checkout_url"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


