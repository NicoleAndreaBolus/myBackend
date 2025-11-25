from django.shortcuts import render, redirect
from registration.models import UserRegistration



def home(request):
    """Render the homepage."""
    return render(request, 'homepage.html')




def login_view(request):
    return render(request, 'registration/login.html')


