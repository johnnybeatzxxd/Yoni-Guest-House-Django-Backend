from django.contrib import admin,messages
from django.utils import timezone
from django.shortcuts import render, redirect
from django import forms
from .models import Rooms, Reservation
# Register your models here.

class UpdatePriceForm(forms.Form):
    new_price = forms.DecimalField(label="New Price", max_digits=10, decimal_places=2)

def update_room_price(modeladmin, request, queryset):
    if 'apply' not in request.POST:
            form = UpdatePriceForm()
            return render(request, 'admin/update_price.html', {'form': form, 'rooms': queryset})
    
    form = UpdatePriceForm(request.POST)
    if form.is_valid():
        new_price = form.cleaned_data['new_price']
        updated_count = queryset.update(price=new_price)
    
        modeladmin.message_user(request, f"Successfully updated price for {updated_count} rooms.", messages.SUCCESS)
        return redirect("..")  # Redirect back to the rooms list page
    else:
        # Show an error message if the form is not valid
        modeladmin.message_user(request, "Error: Invalid form data.", messages.ERROR)
        return render(request, 'admin/update_price.html', {'form': form, 'rooms': queryset})

update_room_price.short_description = "Update price of selected rooms"

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
    actions = [update_room_price]
    def formatted_room_num(self, obj):
        return f"Room {obj.room_num}"
    formatted_room_num.short_description = 'Room Number'

class ReservationAdmin(admin.ModelAdmin):
    list_display = ["formatted_room_num","status","check_in_date","check_out_date","created_at"]
    search_fields = ("guest_first_name","guest_last_name","guest_email","guest_phone",)
    list_filter = [CompletedReservationFilter] 
    def formatted_room_num(self, obj):
        return f"Reservation for {obj.room}"
    formatted_room_num.short_description = 'Reservations'
    pass
    


admin.site.register(Rooms,RoomsAdmin)
admin.site.register(Reservation,ReservationAdmin)