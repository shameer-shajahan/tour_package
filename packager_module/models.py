from django.db import models
# REMOVE this import:
from user_module.models import CustomUser
from django.conf import settings

class Packager(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    company_description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    logo = models.ImageField(upload_to='packager_logos/', null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    established_year = models.PositiveIntegerField(null=True, blank=True)
    license_number = models.CharField(max_length=100, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    reviews = models.TextField(null=True, blank=True)  # Added this field for ReviewForm
    verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-rating']
    
    def __str__(self):
        return f"Packager for {self.user.username}"

class TourPackage(models.Model):
    packager = models.ForeignKey(Packager, on_delete=models.CASCADE, related_name="tour_packages",null=True, blank=True)
    package_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # Duration in days
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='tour_packages/', null=True, blank=True)
    destinations = models.TextField(null=True, blank=True)
    inclusions = models.TextField(null=True, blank=True)
    exclusions = models.TextField(null=True, blank=True)
    itinerary = models.TextField(null=True, blank=True)
    available_dates = models.JSONField(null=True, blank=True)
    capacity_per_date = models.IntegerField(null=True, blank=True)
    min_participants = models.IntegerField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    reviews = models.JSONField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-rating', 'price']
    
    def __str__(self):
        return self.name
    
    def get_available_seats(self, date):
        """
        Check available seats for a given date.
        """
        # Logic to return available seats
        pass
    
    def calculate_total_price(self, num_travelers, add_ons=None, promo_code=None):
        """
        Calculate the final price based on travelers, add-ons, and promo codes.
        """
        total_price = self.price * num_travelers
        if add_ons:
            total_price += sum(add_ons)
        if promo_code:
            # Apply discount if a valid promo code exists
            total_price -= total_price * 0.10  # Example: 10% off for promo code
        return total_price
    
    def is_available(self, date, num_travelers):
        """
        Check if the package is available for the selected date and number of travelers.
        """
        if date in self.available_dates:
            available_capacity = self.capacity_per_date - num_travelers
            if available_capacity >= self.min_participants:
                return True
        return False

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    booking_id = models.CharField(max_length=100, unique=True)
    # Use settings.AUTH_USER_MODEL instead of direct CustomUser reference
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name="bookings")
    booking_date = models.DateTimeField(auto_now_add=True)
    travel_date = models.DateField()
    num_travelers = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending')
    booking_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending' )
    special_requests = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.booking_id} - {self.user.username} - {self.tour_package.name}"