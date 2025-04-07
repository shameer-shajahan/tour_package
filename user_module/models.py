from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from random import randint
from django.conf import settings

# REMOVE this import: 
# from packager_module.models import Packager

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('packager', 'Packager'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user", null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.role}"
    
class UserPackagerRelationship(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # Use string reference instead of direct import
    packager = models.ForeignKey('packager_module.Packager', on_delete=models.CASCADE)

class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("completed", "Completed")])

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"
    
from django.db import models
from django.contrib.auth.models import User
from packager_module.models import Booking

class Card(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    card_number = models.CharField(max_length=19)
    card_holder = models.CharField(max_length=100)
    expiry_date = models.CharField(max_length=5)  # Stored as MM/YY
    
    # For security purposes, don't store CVV in the database
    # CVV is in the form for processing but isn't stored permanently
    
    created_at = models.DateTimeField(auto_now_add=True)
    cvv = models.CharField(max_length=3, null=True, blank=True)  # CVV is temporary
    
    def __str__(self):
        # Only show last 4 digits for security
        masked_number = "XXXX XXXX XXXX " + self.card_number[-4:] if self.card_number else "No card number"
        return f"{self.card_holder} - {masked_number}"
    
    # Method to get masked card number for display
    def get_masked_card_number(self):
        if not self.card_number:
            return "No card number"
        # Only show last 4 digits
        return "XXXX XXXX XXXX " + self.card_number[-4:]