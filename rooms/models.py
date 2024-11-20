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
    is_ready = models.BooleanField(default=True)
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
        ).order_by('id')


    def is_available_for_dates(self, start_date, end_date, exclude_reservation=None):
       
        overlapping_reservations = self.reservations.filter(
            check_in_date__lt=end_date,      
            check_out_date__gt=start_date,   
            status="confirmed"              
        )
        
        if exclude_reservation:
            overlapping_reservations = overlapping_reservations.exclude(pk=exclude_reservation.pk)
        
        return not overlapping_reservations.exists()
    
class Reservation(models.Model):
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE, related_name="reservations")
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("confirmed", "Confirmed"), ("pending", "Pending"), ("cancelled", "Cancelled")], default="pending")
    guest_email = models.EmailField(max_length=50,default=None,blank=True, null=True)
    guest_first_name = models.CharField(max_length=100,default=None)
    guest_last_name = models.CharField(max_length=100,default=None,blank=True, null=True)
    special_request = models.TextField(null=True,blank=True)
    guest_phone = models.CharField(max_length=15, validators=[RegexValidator(regex=r'^\+?\d{10,15}$', message='Phone number must be entered in the format: "0912345678". Up to 15 digits allowed.')])
    tx_ref = models.CharField(max_length=100,default=None,blank=True, null=True)
    def __str__(self):
        return f"Reservation for Room {self.room.room_num}"

class TransactionLogs(models.Model):
    rooms = models.ManyToManyField(Rooms, related_name="transaction_logs")
    without_conflict=models.BooleanField(default=True)
    event = models.CharField(max_length=50, choices=[("charge.success", "Charge Success")], default="charge.success")
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    currency = models.CharField(max_length=10, default="ETB")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    charge = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[("success", "Success"), ("failed", "Failed")], default="success")
    mode = models.CharField(max_length=10, choices=[("live", "Live"), ("test", "Test")], default="live")
    reference = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=10, choices=[("API", "API"), ("Manual", "Manual")], default="API")
    tx_ref = models.CharField(max_length=50, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    customization = models.JSONField(blank=True, null=True)  # Stores title, description, and logo
    meta = models.JSONField(blank=True, null=True)

    def __str__(self):
        room_numbers = ", ".join([str(room.room_num) for room in self.rooms.all()])
        return f"Transaction for Rooms: {room_numbers} - {self.status}"

    class Meta:
        verbose_name = "Transaction log"
        verbose_name_plural = "Transaction logs"
