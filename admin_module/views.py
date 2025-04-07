from django.shortcuts import render,get_object_or_404,redirect

from django.contrib.auth.decorators import login_required




def admin_dashboard(request):
    return render(request, "admin_dashboard.html")





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
import json

from user_module.models import CustomUser
from packager_module.models import Packager, TourPackage, Booking



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
import json

from user_module.models import CustomUser
from packager_module.models import Packager, TourPackage


# Admin access decorator


@login_required
def admin_dashboard(request):
    # Check if user is admin
    if request.user.role != 'admin':
        return redirect('home')  # Redirect non-admin users
    
    # Get counts for dashboard cards
    total_users = CustomUser.objects.count()
    total_packages = TourPackage.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(booking_status='completed').aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    # Get recent bookings
    recent_bookings = Booking.objects.all()
    
    # Monthly bookings data for chart
    now = timezone.now()
    start_date = now - timedelta(days=365)  # Data for the past year
    


    
    # Popular packages for pie chart
    popular_packages = Booking.objects.values(
        'tour_package__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    package_names = [pkg['tour_package__name'] for pkg in popular_packages]
    package_counts = [pkg['count'] for pkg in popular_packages]
    
    context = {
        'total_users': total_users,
        'total_packages': total_packages,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'package_names': json.dumps(package_names),
        'package_booking_counts': json.dumps(package_counts),
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def admin_users(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Filter by role if requested
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'total_users': users.count(),
        'admin_count': CustomUser.objects.filter(role='admin').count(),
        'user_count': CustomUser.objects.filter(role='user').count(),
        'packager_count': CustomUser.objects.filter(role='packager').count(),
    }
    
    return render(request, 'admin_users.html', context)

@login_required
def admin_packages(request):
    packages = TourPackage.objects.all().order_by('-created_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        packages = packages.filter(status=status_filter)
    
    context = {
        'packages': packages,
        'status_filter': status_filter,
        'total_packages': packages.count(),
    }
    
    return render(request, 'admin_packages.html', context)

@login_required
def admin_bookings(request):
    bookings = Booking.objects.all()
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(booking_status=status_filter)
    
    context = {
        'bookings': bookings,
        'status_filter': status_filter,
        'total_bookings': bookings.count(),
        'completed_bookings': Booking.objects.filter(booking_status='completed').count(),
        'pending_bookings': Booking.objects.filter(booking_status='pending').count(),
        'cancelled_bookings': Booking.objects.filter(booking_status='cancelled').count(),
    }
    
    return render(request, 'admin_bookings.html', context)

@login_required
def admin_booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Handle status updates
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'confirmed', 'completed', 'cancelled']:
            booking.booking_status = new_status
            booking.save()
            messages.success(request, f"Booking status updated to {new_status}")
            return redirect('admin_booking_detail', booking_id=booking.id)
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'admin_booking_detail.html', context)

@login_required
def admin_packagers(request):
    packagers = Packager.objects.all()
    
    # Filter by verification status if requested
    verified_filter = request.GET.get('verified')
    if verified_filter:
        is_verified = verified_filter == 'true'
        packagers = packagers.filter(is_verified=is_verified)
    
    context = {
        'packagers': packagers,
        'verified_filter': verified_filter,
        'total_packagers': packagers.count(),
        # 'verified_packagers': Packager.objects.filter(is_verified=True).count(),
        # 'unverified_packagers': Packager.objects.filter(is_verified=False).count(),
    }
    
    return render(request, 'admin_packagers.html', context)

@login_required
def admin_reports(request):
    # Get date range filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Default to last 30 days if no dates provided
    if not start_date:
        end_date_obj = timezone.now()
        start_date_obj = end_date_obj - timedelta(days=30)
        start_date = start_date_obj.strftime('%Y-%m-%d')
        end_date = end_date_obj.strftime('%Y-%m-%d')
    else:
        start_date_obj = timezone.datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = timezone.datetime.strptime(end_date, '%Y-%m-%d')
    
    # Filter bookings by date range
    bookings = Booking.objects.all()
    
    # Calculate revenue
    total_revenue = bookings.all()
    
    # Calculate bookings by package
    package_bookings = bookings.values(
        'tour_package__name'
    ).annotate(
        count=Count('id'),
        revenue=Sum('total_price')
    ).order_by('-count')
    
    # Calculate user registrations in period
    new_users = CustomUser.objects.filter(
        date_joined__gte=start_date_obj,
        date_joined__lte=end_date_obj + timedelta(days=1)
    ).count()
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_bookings': bookings.count(),
        'total_revenue': total_revenue,
        'package_bookings': package_bookings,
        'new_users': new_users,
    }
    
    return render(request, 'admin_reports.html', context)

@login_required
def admin_settings(request):
    # Handle settings updates
    if request.method == 'POST':
        # Example: Update site settings
        # site_name = request.POST.get('site_name')
        # SiteSettings.objects.update_or_create(defaults={'value': site_name}, name='site_name')
        messages.success(request, "Settings updated successfully")
        return redirect('admin_settings')
    
    context = {
        # Add any settings here that need to be displayed/edited
    }
    
    return render(request, 'admin_settings.html', context)