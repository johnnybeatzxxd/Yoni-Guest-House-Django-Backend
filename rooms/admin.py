from django.contrib import admin, messages
from django.utils import timezone
from django.shortcuts import render, redirect
from django import forms
from .models import Rooms, Reservation


class CompletedReservationFilter(admin.SimpleListFilter):
    title = 'Reservation Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('ongoing', 'Ongoing'),
            ('completed', 'Completed'),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'ongoing':
            return queryset.filter(check_out_date__gte=today)
        elif self.value() == 'completed':
            return queryset.filter(check_out_date__lt=today)

class RoomsAdmin(admin.ModelAdmin):
    list_display = ["formatted_room_num", "type", "available_today", "shared_shower", "price"]
    actions = []

    def formatted_room_num(self, obj):
        return f"Room {obj.room_num}"
    formatted_room_num.short_description = 'Room Number'

class ReservationAdmin(admin.ModelAdmin):
    list_display = ["formatted_room_num", "status", "check_in_date", "check_out_date", "created_at"]
    search_fields = ("guest_first_name", "guest_last_name", "guest_email", "guest_phone",)
    list_filter = [CompletedReservationFilter]

    def formatted_room_num(self, obj):
        return f"Reservation for {obj.room}"
    formatted_room_num.short_description = 'Reservations'

admin.site.register(Rooms, RoomsAdmin)
admin.site.register(Reservation, ReservationAdmin)
