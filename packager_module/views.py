from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from .models import Packager,TourPackage,Booking
from user_module.models import CustomUser
from django.contrib.auth.decorators import login_required
from .forms import TourPackageForm
import uuid
from django.http import HttpResponseForbidden



# Create your views here.


@login_required
def packager_dashboard(request):
    try:
        packager = Packager.objects.get(user=request.user)
    except Packager.DoesNotExist:
        return redirect('create_packager_profile')
    
    # Get all packages created by this packager
    packages = TourPackage.objects.filter(packager=packager)
    
    # Get the count of all packages
    package_count = packages.count()
    
    # Get all bookings for packages created by this packager
    # This assumes there's a ForeignKey from Booking to TourPackage
    bookings = Booking.objects.filter(tour_package__in=packages)
    
    # Get the count of all bookings
    booking_count = bookings.count()
    
    # Get the count of completed bookings
    completed_booking_count = bookings.filter(booking_status='completed').count()
    
    context = {
        'data': Packager.objects.filter(user=request.user),
        'package_count': package_count,
        'booking_count': booking_count,
        'completed_booking_count': completed_booking_count
    }
    
    return render(request, 'packager_dashboard.html', context)

@login_required
def delete_package(request, packager_id):

    try:
        # Get the tour package object or return 404 if not found
        tour_package = get_object_or_404(TourPackage, id=packager_id)
        
        # Delete the tour package
        tour_package.delete()
        
        # Add a success message
        messages.success(request, "Tour package successfully deleted.")
    except Exception as e:
        # Handle any errors
        messages.error(request, f"Error deleting tour package: {str(e)}")
    
    # Redirect back to the packager list
    return redirect('packager_list')

@login_required 
def package_detail(request, packager_id):
  
    try:
        # Fetch the specific package with error handling
        package = TourPackage.objects.get(id=packager_id)
        
        # Prepare context data
        context = {
            'package': package
        }
        
        # Render the template with the context
        return render(request, 'package_detail.html', context)
    
    except TourPackage.DoesNotExist:
        # Handle case where package is not found
        messages.error(request, 'The requested package could not be found.')
        return redirect('packager_list')

@login_required    
def packager_booked_list(request):

    try:
            packager = Packager.objects.get(user=request.user)
    except Packager.DoesNotExist:
            return redirect('create_packager_profile')
        
        # Find all tour packages created by this packager
    tour_packages = TourPackage.objects.filter(packager=packager)
        
        # Find all bookings for these tour packages
    bookings = Booking.objects.filter(tour_package__in=tour_packages)
        
    context = {
            'bookings': bookings  # Note: I changed variable name to 'bookings' (plural)
        }
        
    return render(request, 'packager_booked_list.html', context)

@login_required
def upload_package(request):
    # Check if the logged-in user is a packager
 
    try:
        packager = Packager.objects.get(user=request.user)
    except Packager.DoesNotExist:
        return redirect('create_packager_profile')
    
    
    if request.method == 'POST':
        form = TourPackageForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the package but don't save it to the database yet
            package = form.save(commit=False)
            
            # Associate the package with the logged-in packager
            package.packager = packager
            
            # Generate a unique package_id
            package.package_id = f"PKG-{uuid.uuid4().hex[:8].upper()}"
            
            # Save the package to the database
            package.save()
            
            messages.success(request, f"Tour package '{package.name}' has been successfully uploaded.")
            return redirect('packager_list')  # Redirect to packager dashboard or package list
    else:
        form = TourPackageForm()
    
    return render(request, 'upload_package.html', {
        'form': form,
        'title': 'Upload New Tour Package'
    })

@login_required
def update_package(request, package_id):
    # Check if the logged-in user is a packager
    try:
        packager = Packager.objects.get(user=request.user)
    except Packager.DoesNotExist:
        return redirect('create_packager_profile')
    
    # Get the package to update, ensuring it belongs to the current packager
    try:
        package = TourPackage.objects.get(id=package_id, packager=packager)
    except TourPackage.DoesNotExist:
        messages.error(request, "You don't have permission to edit this package or it doesn't exist.")
        return redirect('packager_list')
    
    if request.method == 'POST':
        # Use instance=package to ensure we're updating, not creating new
        form = TourPackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            # Explicitly set packager to prevent ownership changes
            updated_package = form.save(commit=False)
            updated_package.packager = packager
            updated_package.save()
            form.save_m2m()  # Save many-to-many relationships if any
            
            messages.success(request, f"Tour package '{updated_package.name}' has been successfully updated.")
            return redirect('packager_list')  # Redirect to packager dashboard or package list
        else:
            # Show form errors if validation fails
            messages.error(request, "Please correct the errors below.")
    else:
        # Pre-populate the form with existing package data
        form = TourPackageForm(instance=package)
    
    return render(request, 'update_package.html', {
        'form': form,
        'package': package,
        'title': f'Update Tour Package: {package.name}'
    })

@login_required
def create_packager_profile(request):
    """
    View function to handle creating a new packager profile.
    
    Only accessible to authenticated users who don't already have a packager profile.
    Handles initial profile creation with company information and logo upload.
    """
    # Check if user already has a packager profile
    if Packager.objects.filter(user=request.user).exists():
        return redirect('update_packager_profile')
    
    if request.method == 'POST':
        # Extract form data
        company_name = request.POST.get('company_name')
        company_description = request.POST.get('company_description')
        location = request.POST.get('location')
        contact_email = request.POST.get('contact_email')
        contact_phone = request.POST.get('contact_phone')
        website = request.POST.get('website')
        established_year = request.POST.get('established_year')
        license_number = request.POST.get('license_number')
        
        # Create new packager profile
        packager = Packager(
            user=request.user,
            company_name=company_name,
            company_description=company_description,
            location=location,
            contact_email=contact_email,
            contact_phone=contact_phone,
            website=website,
            license_number=license_number
        )
        
        # Handle established_year (could be empty)
        if established_year:
            packager.established_year = int(established_year)
        
        # Handle logo upload if provided
        if 'logo' in request.FILES:
            packager.logo = request.FILES['logo']
        
        # Save the new packager profile
        packager.save()
        
        return redirect('packager_dashboard')  # Redirect to dashboard page
    
    # If GET request, display empty form
    return render(request, 'create_packager_profile.html')

@login_required
def packager_list(request):


    try:
        packager = Packager.objects.get(user=request.user)
    except Packager.DoesNotExist:
        return redirect('create_packager_profile')
    
    user = request.user

    bookings = Booking.objects.filter(user=user)


        # Get the count of all bookings
    booking_count = bookings.count()
    
    # Get the count of completed bookings
    completed_booking_count = bookings.filter(booking_status='completed').count()


    # Get all the tour packages created by the logged-in user's packager
    qs = TourPackage.objects.filter(packager=packager)

    context = {
        'data': qs,
        'booking_count': booking_count,  # Add the count to the context
        'completed_booking_count': completed_booking_count  # Add the completed count
    }
    return render(request, 'packager_list.html', context)

@login_required
def confirm_booking(request, booking_id):
    # Get the booking or return 404 if not found
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.booking_status == "completed":
        return redirect('packager_payment_success')
    
    else:
    # For any request type, update the status
        booking.booking_status = 'confirmed'
        booking.save()
    

    # Redirect to the bookings list
    return redirect('packager_booked_list')

@login_required
def cancelled_booking(request, booking_id):
    # Get the booking or return 404 if not found
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.booking_status == "cancelled":
        return redirect('refund_payment')
    
    else:
    # For any request type, update the status
        booking.booking_status = 'cancelled'
        booking.save()
    

    # Redirect to the bookings list
    return redirect('refund_payment')

@login_required    
def packager_payment_success(request):

    return render(request, 'packager_success.html')

@login_required    
def refund_payment(request):

    return render(request, 'refund_payment.html')



