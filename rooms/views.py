from django.shortcuts import render
from django.http.response import JsonResponse
from .models import Rooms
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

    available_rooms = Rooms.available_rooms(check_in_date, check_out_date)
    available_rooms_data = [{"room_number": room.room_num, "type": room.type, "price_per_night": room.price} for room in available_rooms]

    print(check_in_date,check_out_date)
    rooms = Rooms.objects.filter(type=room_type,available_today=True)
    serilalized_rooms = RoomSerializer(rooms,many=True).data
    return JsonResponse({"rooms":available_rooms_data}, status=200)

