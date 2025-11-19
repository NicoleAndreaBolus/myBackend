from django.urls import path
from registration import views
app_name = "registration" 

urlpatterns = [
       path('api/register/', views.register_user, name='register_user'),
       path('api/users/', views.list_users, name='list_users'),  # new endpoint
       path('api/users/<int:pk>/', views.user_detail, name='user_detail'),

]