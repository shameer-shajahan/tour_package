from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [


    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.admin_users, name='admin_users'),
    path('packages/', views.admin_packages, name='admin_packages'),
    path('bookings/', views.admin_bookings, name='admin_bookings'),
    path('booking/<int:booking_id>/', views.admin_booking_detail, name='admin_booking_detail'),
    path('packagers/', views.admin_packagers, name='admin_packagers'),
    path('reports/', views.admin_reports, name='admin_reports'),
    path('settings/', views.admin_settings, name='admin_settings'),

 ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
