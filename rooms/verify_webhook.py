import uuid
from Crypto.Hash import HMAC, SHA256
import os
import os
from dotenv import load_dotenv
import json

load_dotenv()


def verify_webhook(request):
    secret = os.getenv("CHAPA_SECRET")
    chapa_signature = request.headers.get('Chapa-Signature')
    x_chapa_signature = request.headers.get('x-chapa-signature')
    
    if not chapa_signature or not x_chapa_signature:
        return "error: Missing signature headers"
    
    # Verify Chapa-Signature
    chapa_hash = HMAC.new(secret.encode(), secret.encode(), digestmod=SHA256).hexdigest()
    
    # Verify x-chapa-signature 
    payload_hash = HMAC.new(secret.encode(), request.body, digestmod=SHA256).hexdigest()
    
    # Validate both signatures
    if chapa_hash == chapa_signature and payload_hash == x_chapa_signature:
        return True
    else: 
        return False