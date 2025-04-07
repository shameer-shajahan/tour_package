# urls.py
from django.urls import path
from . import views

urlpatterns = [

    path('', views.index_view, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user_packager_list/', views.user_packager_list, name='user_packager_list'),
    path('user_packages_list/', views.user_packages_list, name='user_packages_list'),
    path('user_packager_packages_list/<int:package_id>/', views.user_packager_packages_list, name='user_packager_packages_list'),
    path('packages/<int:package_id>/', views.user_package_detail, name='user_package_detail'),
    path('book/<int:package_id>/', views.book_tour_package, name='book'),
    path('user_booked_list/', views.user_booked_list, name='user_booked_list'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('bookings/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/refund/', views.refund, name='refund'),
    path('card_input/<int:booking_id>/', views.card_input, name='card_input'),

    ]