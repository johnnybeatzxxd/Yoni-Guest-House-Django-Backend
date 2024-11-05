from django.db import models

# Create your models here.
class Rooms(models.Model):
    room_num = models.IntegerField()
    type = models.CharField(
        max_length=50,
        choices=[('single', 'Single'),('double', 'Double')])
    desc = models.TextField()
    images = models.JSONField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.JSONField()
    available_today = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
    def __str__(self):
        return f"Room {self.room_num}"