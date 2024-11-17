from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from .models import Rooms,Reservation,TransactionLogs
from .serializers import RoomSerializer
from rest_framework.decorators import api_view
from django.utils.dateparse import parse_datetime
from datetime import datetime, date
from .payment import initiate_payment
import uuid
from .verify_webhook import verify_webhook

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
    available_rooms_data = [{"room_number": room.room_num, "type": room.type, "price_per_night": room.price,"discription":room.desc,"images":room.images,"aminities":room.amenities,"available_today":room.is_ready} for room in available_rooms]

    print(check_in_date,check_out_date)
    return JsonResponse({"rooms":available_rooms_data}, status=200)

@api_view(['POST'])
def book_reservation(request):
    
    check_in_date_str = request.data.get("from")
    check_out_date_str = request.data.get("to")
    room_nums = request.data.get("rooms")
    guest_email = request.data.get("email")
    special_request = request.data.get("specialRequest")
    guest_first_name = request.data.get("firstName")
    guest_last_name = request.data.get("lastName")
    guest_phone = request.data.get("phoneNumber")

    try:
        check_in_date = datetime.strptime(check_in_date_str, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(check_out_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)


    today = date.today()
    print(today)
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
            tx_ref = tx_ref
        )
        amount += int(room.price)

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
    
    is_request_valid = verify_webhook(request)
    # Validate both signatures
    if is_request_valid:
        event = request.data.get("event")

        if event == "charge.success":
            
            tx_ref = request.data.get("tx_ref")
            reserved_rooms = Reservation.objects.filter(tx_ref=tx_ref)
            without_conflict = True

            for reserved_room in reserved_rooms:
                room = reserved_room.room
                reserved_room.status = "confirmed"
                is_available = room.is_available_for_dates(reserved_room.check_in_date,reserved_room.check_out_date)
                if not is_available:
                    without_conflict = False
                reserved_room.save()
            
            log = TransactionLogs.objects.create(
                event=request.data.get("event"),
                without_conflict=without_conflict,
                type=request.data.get("type"),
                status=request.data.get("status"),
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                email=request.data.get("email"),
                mobile=request.data.get("mobile"),
                currency=request.data.get("currency"),
                amount=request.data.get("amount"),
                charge=request.data.get("charge"),
                reference=request.data.get("reference"),
                tx_ref=request.data.get("tx_ref"),
                payment_method=request.data.get("payment_method"),
                customization=request.data.get("customization"),  
                meta=request.data.get("meta"),  
                created_at=parse_datetime(request.data.get("created_at")),  
                updated_at=parse_datetime(request.data.get("updated_at")),  
            )
            rooms = [reservation.room for reservation in reserved_rooms]
            log.rooms.set(rooms)

        print("Event validated and received:", event)
        
        return JsonResponse({"status": "Event processed"}, status=200)
    else:
        return JsonResponse({"error": "Invalid signature"}, status=400)

