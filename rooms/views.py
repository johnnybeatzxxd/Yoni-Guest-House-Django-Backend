from django.shortcuts import render
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Rooms,Reservation
from .serializers import RoomSerializer
from rest_framework.decorators import api_view
from datetime import datetime, date

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
    guest_number = request.data.get("guestNumber")
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

    for room in available_rooms:
        reservation = Reservation.objects.create(
            room=room,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            status="confirmed",
            guest_email=guest_email, 
            guest_first_name=guest_first_name,
            guest_last_name=guest_last_name,
            guest_phone=guest_phone,
            guests=guest_number
        )

        if check_in_date == today:
            room.available_today = False
            room.save()

    return JsonResponse({
        "message": "Reservations created successfully!",
        "reserved_rooms": [room.room_num for room in available_rooms]
    }, status=200)