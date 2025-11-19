from django.shortcuts import render, redirect
from registration.models import UserRegistration



def home(request):
    """Render the homepage."""
    return render(request, 'homepage.html')




def login_view(request):
    """Login view that supports GET and POST.


    GET: render login.html
    POST: accept either 'username' or 'email' as the identifier and 'password'.
    - If credentials match a UserRegistration record, store user_id (and username)
      in the session and redirect to the user list page.
    - If not, re-render login.html with a generic error message.
    """
    error = ''
    if request.method == 'POST':
        # Accept either "username" or "email" field from the form
        identifier = request.POST.get('username', '').strip() or request.POST.get('email', '').strip()
        password = request.POST.get('password', '')


        user = None
        if identifier:
            # Try to find by email first, then by username.
            # Adjust field names if your model uses different attribute names.
            try:
                user = UserRegistration.objects.get(email=identifier)
            except UserRegistration.DoesNotExist:
                try:
                    user = UserRegistration.objects.get(username=identifier)
                except UserRegistration.DoesNotExist:
                    user = None


        # Note: This example assumes passwords are stored in plaintext on the model
        # (as in the original demo). In production, use Django's auth system or
        # properly hashed passwords.
        if user and user.password == password:
            request.session['user_id'] = user.id
            # store a friendly name for display later (optional)
            request.session['username'] = getattr(user, 'username', user.email)
            return redirect('user_list')  # expects a URL pattern named 'user_list'
        else:
            error = 'Invalid username or password.'


    # GET requests or failed POST come here
    return render(request, 'login.html', {'error': error})




def logout_view(request):
    """Clear the session and redirect to login page."""
    request.session.pop('user_id', None)
    request.session.pop('username', None)
    return redirect('login')  # expects a URL pattern named 'login'




def user_list_view(request):
    """Display a list of users to authenticated visitors.


    - If there's no user_id in the session, redirect to login.
    - Otherwise, retrieve all UserRegistration records and render user_list.html.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # expects a URL pattern named 'login'


    users = UserRegistration.objects.all()
    return render(request, 'user_list.html', {'users': users})