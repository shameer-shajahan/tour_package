from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [


    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.admin_users, name='admin_users'),
    path('packages/<int:package_id>/', views.admin_package_detail, name='admin_package_detail'),
    path('packages/', views.admin_packages, name='admin_packages'),
    path('bookings/', views.admin_bookings, name='admin_bookings'),
    path('booking/<int:booking_id>/', views.admin_booking_detail, name='admin_booking_detail'),
    path('packagers/', views.admin_packagers, name='admin_packagers'),
    path('reports/', views.admin_reports, name='admin_reports'),
    path('settings/', views.admin_settings, name='admin_settings'),
    path('admin/packagers/delete/<int:packager_id>/', views.delete_packager, name='delete_packager'),
    path('admin/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin_packages_list/<int:package_id>/', views.admin_packages_list, name='admin_packages_list'),
    path('package/delete/<int:packager_id>/', views.admin_delete_package, name='admin_delete_package'),

 ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
