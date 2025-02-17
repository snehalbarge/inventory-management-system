from django.db import models
from django.core.exceptions import ValidationError

class Member(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    booking_count = models.IntegerField(default=0)
    date_joined = models.DateTimeField()
    
    def __str__(self):
        return self.name
    
    def get_active_bookings_count(self):
        return self.booking_set.count()

class Inventory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    remaining_count = models.IntegerField()
    expiration_date = models.DateField()
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.remaining_count < 0:
            raise ValidationError("Remaining count cannot be negative")
        super().save(*args, **kwargs)

class Booking(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    item = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    booking_datetime = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.member.name} - {self.item.name}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only check on creation
            if self.member.get_active_bookings_count() >= 2:
                raise ValidationError("Member has reached maximum booking limit")
            if self.item.remaining_count <= 0:
                raise ValidationError("Item is out of stock")
            self.item.remaining_count -= 1
            self.item.save()
        super().save(*args, **kwargs)