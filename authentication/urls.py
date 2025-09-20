from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('token-info/', views.token_info_view, name='token_info'),
    path('create-app/', views.create_oauth_application_view, name='create_app'),
    path('health/', views.health_check_view, name='health_check'),
]
