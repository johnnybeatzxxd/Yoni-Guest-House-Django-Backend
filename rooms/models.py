from django.db import models
from django.core.validators import RegexValidator

# Create your models here.
class Rooms(models.Model):
    room_num = models.IntegerField()
    type = models.CharField(max_length=50,choices=[('single', 'Single'),('double', 'Double')])
    desc = models.TextField()
    images = models.JSONField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.JSONField()
    available_today = models.BooleanField(default=True)
    shared_shower = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
    
    def __str__(self):
        return f"Room {self.room_num}"
    
    @classmethod
    def available_rooms(self, check_in_date, check_out_date):
        return self.objects.exclude(
            reservations__check_in_date__lt=check_out_date,
            reservations__check_out_date__gt=check_in_date,
            reservations__status="confirmed"
        )


    def is_available_for_dates(self, start_date, end_date):
       
        overlapping_reservations = self.reservations.filter(
            check_in_date__lt=end_date,      
            check_out_date__gt=start_date,   
            status="confirmed"              
        )
        return not overlapping_reservations.exists()
    
class Reservation(models.Model):
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE, related_name="reservations")
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    guests = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("confirmed", "Confirmed"), ("pending", "Pending"), ("cancelled", "Cancelled")], default="pending")
    guest_email = models.EmailField(max_length=50,default=None)
    guest_first_name = models.CharField(max_length=100,default=None)
    guest_last_name = models.CharField(max_length=100,default=None)
    guest_phone = models.CharField(max_length=15, validators=[RegexValidator(regex=r'^\+?\d{10,15}$', message='Phone number must be entered in the format: "0912345678". Up to 15 digits allowed.')])
    def __str__(self):
        return f"Reservation for Room {self.room.room_num}"
