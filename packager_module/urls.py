from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [

    path('packager_dashboard/', views.packager_dashboard, name='packager_dashboard'),
    path('packager_list/', views.packager_list, name='packager_list'),
    path('upload_package/', views.upload_package, name='upload_package'),
    path('package/delete/<int:packager_id>/', views.delete_package, name='delete_package'),
    path('package/detail/<int:packager_id>/', views.package_detail, name='package_detail'),
    path('package/update/<int:package_id>/', views.update_package, name='update_package'),
    path('packager/packager_booked_list/', views.packager_booked_list, name='packager_booked_list'),
    path('create_packager_profile', views.create_packager_profile, name='create_packager_profile'),
    path('bookings/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('payment/success/', views.packager_payment_success, name='packager_payment_success'),
    path('payment/cancell/<int:booking_id>/', views.cancelled_booking, name='cancelled_booking'),
    path('payment/refund/', views.refund_payment, name='refund_payment'),

 ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
