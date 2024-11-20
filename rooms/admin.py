from django.contrib import admin, messages
from django.utils import timezone
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django import forms
from datetime import date
from .models import Rooms, Reservation, TransactionLogs


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
    list_display = ["formatted_room_num", "type", "is_ready", "price"]
    actions = []

    def formatted_room_num(self, obj):
        return f"Room {obj.room_num}"
    formatted_room_num.short_description = 'Room Number'

from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        status = cleaned_data.get('status')
        is_form_valid = True

        if check_in_date and check_out_date:
            today = date.today()
            if check_in_date < today:
                self.add_error('check_in_date', "Check-in date must be earlier than check-out date.")
                is_form_valid = False

            if check_in_date >= check_out_date:
                self.add_error('check_out_date', "Check-out date must be later than check-in date.")
                is_form_valid = False

            if status == "confirmed":
                if self.instance.pk is None:
                    if room and not room.is_available_for_dates(check_in_date, check_out_date):
                        raise forms.ValidationError(
                            f"The room {room.room_num} is not available from {check_in_date} to {check_out_date}."
                        )
        
        if self.instance.pk is None:
            action = "Creating"
        else:
            action = "Editing"
        
        if self.instance.pk is None and status != "confirmed":
            self.add_error('status', "Reservation must be confirmed.")
            is_form_valid = False
        
        if not self.instance.pk is None and status == "pending":
            self.add_error('status', "Reservation must be confirmed or cancelled.")
            is_form_valid = False
        
        # edit mode    
        if self.instance.pk is not None: 
            original_check_in_date = self.instance.check_in_date
            original_check_out_date = self.instance.check_out_date
            # check if the date is changed if changed check for the room availability
            
            if check_in_date != original_check_in_date or check_out_date != original_check_out_date:
                print("checking the availability")
                if room and not room.is_available_for_dates(check_in_date, check_out_date, exclude_reservation=self.instance):
                    raise forms.ValidationError(
                        f"The room {room.room_num} is not available from {check_in_date} to {check_out_date}."
                    )
                
        if not is_form_valid:
            raise forms.ValidationError("The form is invalid.")
            
        return cleaned_data

class ReservationAdmin(admin.ModelAdmin):
    form = ReservationForm
    list_display = ["formatted_room_num", "status", "check_in_date", "check_out_date", "created_at"]
    search_fields = ("guest_first_name", "guest_last_name", "guest_email", "guest_phone",)
    list_filter = [CompletedReservationFilter]


    def formatted_room_num(self, obj):
        return f"Reservation for {obj.room}"
    formatted_room_num.short_description = 'Reservations'

class TransactionLogsAdmin(admin.ModelAdmin):
    list_display = ["formatted_room_nums", "status", "without_conflict", "mobile","payment_method", "amount", "charge", "created_at"]
    search_fields = ("mobile","first_name","last_name","email","amount",)
    def formatted_room_nums(self, obj):
        room_numbers = [str(room.room_num) for room in obj.rooms.all()]
        return f"Rooms {', '.join(room_numbers)}"
    formatted_room_nums.short_description = 'Reservations'

admin.site.site_header = "Yoni Administration"
admin.site.register(Rooms, RoomsAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(TransactionLogs,TransactionLogsAdmin)
