from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST.get('email', '') # Get email with empty default if not provided
        first_name = request.POST.get('first_name', '') # Get first name
        last_name = request.POST.get('last_name', '') # Get last name
        role = 'customer'
        
        # Create user with all fields
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create profile for the user
        from customer.models import UserProfile
        try:
            profile = user.profile
        except:
            profile = UserProfile.objects.create(user=user)
        
        if user.is_superuser:
            return redirect('/admin/')
        
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)
        
        login(request, user)
        
        if role == 'customer':
            return redirect('customer:customer-dashboard')
        else:
            return redirect('provider:provider-dashboard')
    
    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user has a profile, create one if not
            from customer.models import UserProfile
            try:
                # Try to access the profile
                profile = user.profile
            except:
                # Create profile if it doesn't exist
                profile = UserProfile.objects.create(user=user)
                print(f"Created profile for user {user.username}")
            
            login(request, user)
            
            if user.is_superuser:
                return redirect('/admin/')
            elif user.groups.filter(name='customer').exists():
                return redirect('customer:customer-dashboard')
            else:
                return redirect('provider:provider-dashboard')
        
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def customer_dashboard(request):
    return render(request, 'customer/dashboard.html')


@login_required
def provider_dashboard(request):
    return render(request, 'provider/dashboard.html')


def policies_view(request):
    return render(request, 'policies.html')


def contact_view(request):
    return render(request, 'contact.html')
