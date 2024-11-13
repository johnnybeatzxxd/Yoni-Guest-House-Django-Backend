from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from .models import Rooms,Reservation
from .serializers import RoomSerializer
from rest_framework.decorators import api_view
from datetime import datetime, date
from .payment import initiate_payment
import uuid
from Crypto.Hash import HMAC, SHA256
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Create your views here.
@api_view(['POST'])
def available_rooms(request):
    print(request.data)

    room_type = request.data.get("type")
    check_in_date_str = request.data.get("from")
    check_out_date_str = request.data.get("to")
    
    check_in_date = datetime.strptime(check_in_date_str, "%Y-%m-%d").date()
    check_out_date = datetime.strptime(check_out_date_str, "%Y-%m-%d").date()
    
    today = date.today()
    if check_in_date < today:
        return JsonResponse({"error": "check in date cannot be in the past."}, status=400)
    
    if check_out_date <= check_in_date:
        return JsonResponse({"error": "check out date must be after check-in date."}, status=400)

    available_rooms = Rooms.available_rooms(check_in_date, check_out_date).filter(type=room_type)
    available_rooms_data = [{"room_number": room.room_num, "type": room.type, "price_per_night": room.price,"discription":room.desc,"images":room.images,"aminities":room.amenities,"available_today":room.available_today} for room in available_rooms]

    print(check_in_date,check_out_date)
    return JsonResponse({"rooms":available_rooms_data}, status=200)

@api_view(['POST'])
def book_reservation(request):
    
    check_in_date_str = request.data.get("from")
    check_out_date_str = request.data.get("to")
    room_nums = request.data.get("rooms")
    guest_email = request.data.get("email")
    special_request = request.data.get("specialRequest")
    adult_number = request.data.get("adultNumber")
    children_number = request.data.get("childrenNumber")
    guest_first_name = request.data.get("firstName")
    guest_last_name = request.data.get("lastName")
    guest_phone = request.data.get("phoneNumber")

    try:
        check_in_date = datetime.strptime(check_in_date_str, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(check_out_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)


    today = date.today()
    if check_in_date < today:
        return JsonResponse({"error": "Check-in date cannot be in the past."}, status=400)

    if check_out_date <= check_in_date:
        return JsonResponse({"error": "Check-out date must be after check-in date."}, status=400)


    unavailable_rooms = []
    available_rooms = []
    for room_num in room_nums:
        room = Rooms.objects.filter(room_num=room_num).first()
        if not room:
            return JsonResponse({"error": f"Room with number {room_num} does not exist."}, status=404)
        
        if not room.is_available_for_dates(check_in_date, check_out_date):
            unavailable_rooms.append(room_num)
        else:
            available_rooms.append(room)

    if unavailable_rooms:
        return JsonResponse({
            "error": "Some rooms are not available for the selected dates.",
            "unavailable_rooms": unavailable_rooms
        }, status=400)
    amount = 0
    
    tx_ref = str(uuid.uuid4())
    for room in available_rooms:
        reservation = Reservation.objects.create(
            room=room,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            status="pending",
            guest_email=guest_email, 
            guest_first_name=guest_first_name,
            guest_last_name=guest_last_name,
            guest_phone=guest_phone,
            special_request=special_request,
            adult_number=adult_number,
            children_number=children_number,
            tx_ref = tx_ref

        )
        amount += int(room.price)
        
        if check_in_date == today:
            room.available_today = False
            room.save()

    total_stay_days = (check_out_date - check_in_date).days
    amount = amount * total_stay_days 
    discription = f"Reservation Payment {amount} ETB "

    payment_url = initiate_payment(guest_first_name,guest_last_name,guest_email,guest_phone,amount,discription,tx_ref)
    return JsonResponse({
        "message": "Reservations created successfully!",
        "reserved_rooms": [room.room_num for room in available_rooms],
        "payment_url": payment_url
    }, status=200)


@api_view(['POST', 'GET'])
def payment_received(request):

    secret = os.getenv("CHAPA_SECRET")
    chapa_signature = request.headers.get('Chapa-Signature')
    x_chapa_signature = request.headers.get('x-chapa-signature')
    
    if not chapa_signature or not x_chapa_signature:
        return JsonResponse({"error": "Missing signature headers"}, status=400)
    
    # Verify Chapa-Signature
    chapa_hash = HMAC.new(secret.encode(), secret.encode(), digestmod=SHA256).hexdigest()
    
    # Verify x-chapa-signature 
    payload_hash = HMAC.new(secret.encode(), request.body, digestmod=SHA256).hexdigest()
    
    # Validate both signatures
    if chapa_hash == chapa_signature and payload_hash == x_chapa_signature:
        event = request.data.get("event")
        tx_ref = request.data.get("tx_ref")
        if event == "charge.success":
            print("updating the db")
            reserved_room = Reservation.objects.get(tx_ref=tx_ref)
            reserved_room.status = "confirmed"
            reserved_room.save()

        print("Event validated and received:", event)
        
        return JsonResponse({"status": "Event processed"}, status=200)
    else:
        return JsonResponse({"error": "Invalid signature"}, status=400)

def approve_payment(request):
    """"
        handles payment approval of room booking
        returns: status code 200 if success, otherwise 400
    """
    # check if room is availabe from reservation
    print(request.body)

    return HttpResponse(status=200)