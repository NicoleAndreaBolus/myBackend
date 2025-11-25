from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password


from .models import UserRegistration
from .serializer import RegistrationSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def register_user(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_users(request):
    users = UserRegistration.objects.all()
    serializer = RegistrationSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    try:
        user = UserRegistration.objects.get(pk=pk)
    except UserRegistration.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RegistrationSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = RegistrationSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print("Serializer errors:", serializer.errors)  # 👈 See real reason in your terminal
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# ---------- LOGIN ----------
def login_view(request):
    if request.method == "GET":
        if request.session.get("user_id"):
            return redirect('registration:users_html')
        return render(request, 'registration/login.html')

    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')

    if not email or not password:
        messages.error(request, "Enter both email and password.")
        return render(request, 'registration/login.html', {'email': email})

    try:
        user = UserRegistration.objects.get(email=email)
    except UserRegistration.DoesNotExist:
        messages.error(request, "Invalid credentials.")
        return render(request, 'registration/login.html', {'email': email})

    if check_password(password, user.password):
        request.session['user_id'] = user.id
        request.session['user_name'] = f"{user.first_name} {user.last_name}"
        return redirect('registration:users_html')

    if user.password == password:
        user.password = make_password(password)
        user.save(update_fields=['password'])
        request.session['user_id'] = user.id
        request.session['user_name'] = f"{user.first_name} {user.last_name}"
        return redirect('registration:users_html')

    messages.error(request, "Invalid credentials.")
    return render(request, 'registration/login.html', {'email': email})


# ---------- LOGOUT ----------
def logout_view(request):
    request.session.flush()
    return redirect('home_html')


# ---------- LOGIN REQUIRED DECORATOR ----------
def login_required_view(fn):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect(f"{reverse('registration:login_html')}?next={request.path}")
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper


# ---------- USERS LIST ----------
@login_required_view
def users_html(request):
    users = UserRegistration.objects.all().order_by('id')
    return render(request, 'registration/users_list.html', {
        'users': users,
        'current_user': request.session.get('user_name')
    })

# ---------- CREATE USER ----------
@login_required_view
def user_create_html(request):
    if request.method == 'POST':
   
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        gender = request.POST.get('gender', '').strip()
        profile_picture = request.FILES.get('profile_picture') 

    
        if not first_name or not last_name or not email or not password:
            messages.error(request, "First name, last name, email and password are required.")
            return render(request, 'registration/user_form.html', {
                'title': 'Add User',
                'user': None,  
            })

      
        user = UserRegistration(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,   
            gender=gender,
        )

        if profile_picture:
            user.profile_picture = profile_picture

        user.save()

        messages.success(request, "User created successfully.")
        return redirect('registration:users_html')


    return render(request, 'registration/user_form.html', {
        'title': 'Add User',
        'user': None,
    })

# ---------- UPDATE USER ----------
@login_required_view
def user_update_html(request, pk):
    user = get_object_or_404(UserRegistration, pk=pk)

    if request.method == 'POST':
     
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        gender = request.POST.get('gender', '').strip()
        profile_picture = request.FILES.get('profile_picture')

  
        if not first_name or not last_name or not email:
            messages.error(request, "First name, last name and email are required.")
            return render(request, 'registration/user_form.html', {
                'title': 'Edit User',
                'user': user,
            })


        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.gender = gender

   
        if password:
            user.password = password

        if profile_picture:
            user.profile_picture = profile_picture

        user.save()

        messages.success(request, "User updated successfully.")
        return redirect('registration:users_html')


    return render(request, 'registration/user_form.html', {
        'title': 'Edit User',
        'user': user,
    })

# ---------- DELETE USER ----------
@login_required_view
def user_delete_html(request, pk):
    user = get_object_or_404(UserRegistration, pk=pk)

    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('registration:users_html')

    return render(request, 'registration/user_confirm_delete.html', {
        'user': user
    })