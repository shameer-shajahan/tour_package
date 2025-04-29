from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django import forms
from .models import CustomUser 
from packager_module.models import TourPackage, Packager, Booking
from .forms import BookingForm,CardForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
import uuid
from .forms import BookingForm, UserProfileForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator



 # Use CustomUser model

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=[('user', 'Regular User'), ('packager', 'Packager')])

    class Meta:
        model = CustomUser  # Use CustomUser directly
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create the user object (CustomUser instance)
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Set the password
            user.save()  # Save the user object
            
            # Create the user profile with the selected role
            role = form.cleaned_data['role']
            user.role = role
            user.save()  # Save the role on the CustomUser instance

            # Log the user in
            login(request, user)
            messages.success(request, f"Registration successful! You are registered as a {role}.")

            # Redirect based on role
            if role == 'packager':
                return redirect('packager_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, "Registration failed. Please correct the errors.")
    else:
        form = UserRegistrationForm()

    return render(request, 'index.html', {'form': form})

def login_view(request):
    """
    View for user login.
    After successful login, redirects based on user's role.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authenticate user
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Get user role from CustomUser model and redirect accordingly
                try:
                    user_profile = CustomUser.objects.get(username=user.username)
                    role = user_profile.role
                    
                    messages.info(request, f"You are now logged in as {username} ({role}).")
                    
                    if role == 'packager':
                        return redirect('/packager/packager_dashboard/')
                    elif role == "admin":
                        return redirect("/admin_module/dashboard/")
                    else:
                        return redirect('user_dashboard')
                except CustomUser.DoesNotExist:
                    # Fallback if profile doesn't exist
                    messages.info(request, f"You are now logged in as {username}.")
                    return redirect('user_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'index.html', {'form': form})

def logout_view(request):
    """
    View for user logout.
    """
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('index')

def user_dashboard(request):
    # Fetch all packagers and tour packages
    packagers = Packager.objects.all()
    tour_packages = TourPackage.objects.all()

    # Pagination for Tour Packages
    tour_paginator = Paginator(tour_packages, 4)  # Show 3 packages per page
    tour_page_number = request.GET.get('tour_page')  # Get the current page number for tour packages
    tour_page_obj = tour_paginator.get_page(tour_page_number)

    # Pagination for Packagers
    packager_paginator = Paginator(packagers, 4)  # Show 5 packagers per page
    packager_page_number = request.GET.get('packager_page')  # Get the current page number for packagers
    packager_page_obj = packager_paginator.get_page(packager_page_number)

    # Add both paginated objects to context
    context = {
        'user': request.user,
        'packagers': packager_page_obj,
        'tour_packages': tour_page_obj,
    }

    return render(request, 'user_dashboard.html', context)

def index_view(request):
    return render(request, 'index.html', {'user': request.user})

def user_packager_list(request):

    qs=Packager.objects.all()

    return render(request, 'user_packager_list.html', {'user': request.user, 'data': qs})

def user_packages_list(request):

    qs=TourPackage.objects.all()

    return render(request, 'user_packages_list.html', {'user': request.user, 'data': qs})

def user_packager_packages_list(request , package_id):

    qs = TourPackage.objects.filter(packager=package_id)

    # Return the rendered page with the filtered tour packages
    return render(request, 'user_packager_packages_list.html', {'user': request.user, 'data': qs})

def user_package_detail(request, package_id):
  
    try:
        # Fetch the specific package with error handling
        package = TourPackage.objects.get(id=package_id)
        
        # Prepare context data
        context = {
            'package': package
        }
        
        # Render the template with the context
        return render(request, 'user_package_detail.html', context)
    
    except TourPackage.DoesNotExist:
        # Handle case where package is not found
        messages.error(request, 'The requested package could not be found.')
        return redirect('user_packages_list')

def book_tour_package(request, package_id):
    tour_package = get_object_or_404(TourPackage, id=package_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Create booking instance
            booking = form.save(commit=False)
            booking.user = request.user
            booking.tour_package = tour_package
            
            # Generate unique booking ID
            booking.booking_id = str(uuid.uuid4())[:8].upper()
            
            # Calculate total price
            booking.total_price = tour_package.price * form.cleaned_data['num_travelers']
            
            # Set default status
            booking.booking_status = 'pending'
            booking.payment_status = 'pending'
            
            booking.save()
            
            messages.success(request, f'Booking confirmed! Your Booking ID is {booking.booking_id}')
            return redirect('user_booked_list')  # Redirect to user's bookings page
    else:
        form = BookingForm()
    
    context = {
        'form': form,
        'tour_package': tour_package
    }
    return render(request, 'book_package.html', context)

def user_booked_list(request):
    # Get the current logged-in user
    user = request.user
    
    # Find all bookings made by this user
    bookings = Booking.objects.filter(user=user)
    
    # Get the count of bookings
    booking_count = bookings.count()
    
    context = {
        'bookings': bookings,
        'booking_count': booking_count  # Add the count to the context
    }
    
    return render(request, 'user_booked_list.html', context)

def user_profile(request):
    """
    View user profile information
    """
    user = request.user

    bookings = Booking.objects.filter(user=user)
    
    # Get the count of all bookings
    booking_count = bookings.count()
    
    # Get the count of completed bookings
    completed_booking_count = bookings.filter(booking_status='completed').count()
    
    # Add any additional profile data you want to display
    context = {
        'user': user,
        'booking_count': booking_count,  # Add the count to the context
        'completed_booking_count': completed_booking_count  # Add the completed count
    }
    return render(request, 'user_profile.html', context)

def update_profile(request):
    """
    Update user profile information
    """
    user = request.user

    bookings = Booking.objects.filter(user=user)
    
    # Get the count of bookings
    booking_count = bookings.count()

    completed_booking_count = bookings.filter(booking_status='completed').count()
    
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'bookings': bookings,
        'booking_count': booking_count,  # Add the count to the context
        'completed_booking_count': completed_booking_count  # Add the completed count
        
    }
    return render(request, 'update_profile.html', context)

def change_password(request):
    """
    Change user password
    """
    user = request.user

    bookings = Booking.objects.filter(user=user)


        # Get the count of all bookings
    booking_count = bookings.count()
    
    # Get the count of completed bookings
    completed_booking_count = bookings.filter(booking_status='completed').count()

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important! Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'booking_count': booking_count,  # Add the count to the context
        'completed_booking_count': completed_booking_count  # Add the completed count
    }
    return render(request, 'change_password.html', context)

def delete_booking(request, booking_id):

    try:
        # Get the tour package object or return 404 if not found
        booking = get_object_or_404(Booking, id=booking_id)  
     
        # Delete the tour package
        booking.delete()

        if booking.booking_status == "completed":
            return redirect('refund') 
        
        # Add a success message
        messages.success(request, "Tour booking successfully deleted.")
    except Exception as e:
        # Handle any errors
        messages.error(request, f"Error deleting tour booking: {str(e)}")
    
    # Redirect back to the packager list
    return redirect('user_booked_list')

def payment_success(request):

    return render(request, 'success.html')

def card_input(request, booking_id):
    user = request.user
    
    # Find the specific booking
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if booking is already completed
    if booking.booking_status == "completed":
        return redirect('payment_success')
    
    if booking.booking_status == "pending":
        return redirect('user_booked_list')

    if request.method == 'POST':
        form = CardForm(request.POST, request.FILES)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = user
            card.booking = booking
            card.save()
            booking.booking_status = 'completed'
            booking.save()
            return redirect('payment_success')
    else:
        # For GET requests, create an empty form
        form = CardForm()
        
    context = {
        'booking': booking,
        'form': form
    }

    return render(request, 'card_input.html', context)

def refund(request):
    
    return render(request, 'refund.html')

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from .models import CustomUser  # Import your custom user model

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            
            # Generate token and uid
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Prepare email
            subject = 'Password Reset Request'
            email_template = 'reset_password_email.html'
            email_context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'TRAVELIX',
            }
            
            html_message = render_to_string(email_template, email_context)
            plain_message = f"Hi {user.username}, click this link to reset your password: {reset_url}"
            
            # Send email
            send_mail(
                subject,
                plain_message,
                'noreply@yourwebsite.com',
                [email],
                html_message=html_message,
                fail_silently=False
            )
            
            messages.success(request, "Password reset link has been sent to your email.")
            return redirect('login')
            
        except CustomUser.DoesNotExist:
            messages.error(request, "No account found with that email address.")
    
    return render(request, 'forgot_password.html')

def password_reset_confirm(request, uidb64, token):
    try:
        # Decode the user id
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        
        # Verify token
        if not default_token_generator.check_token(user, token):
            messages.error(request, "Password reset link is invalid or has expired.")
            return redirect('forgot_password')
        
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 != password2:
                messages.error(request, "Passwords don't match.")
                return render(request, 'password_reset_confirm.html')
            
            # Set new password
            user.set_password(password1)
            user.save()
            
            messages.success(request, "Password has been reset successfully. You can now log in with your new password.")
            return redirect('login')
            
        return render(request, 'password_reset_confirm.html')
        
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        messages.error(request, "Password reset link is invalid.")
        return redirect('forgot_password')
   
