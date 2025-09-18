# accounts/urls.py (updated)
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='accounts.signup'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('orders/', views.orders, name='accounts.orders'),
    path('settings/', views.settings, name='accounts.settings'),
    path('security-questions/', views.setup_security_questions, name='accounts.setup_security'),
    path('forgot-password/', views.forgot_password, name='accounts.forgot_password'),
    path('verify-security/<int:user_id>/', views.verify_security_answers, name='accounts.verify_security'),
    path('reset-password/', views.reset_password, name='accounts.reset_password'),
]