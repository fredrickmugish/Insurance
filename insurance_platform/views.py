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
        
        role = 'customer'

        user = User.objects.create_user(username=username, password=password)
        
        if user.is_superuser:
            return redirect('/admin/')
        
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)
        login(request, user)
        
        if role == 'customer':
            return redirect('/customer/dashboard/')
        else:
            return redirect('/provider/dashboard/')
            
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('/admin/')
            elif user.groups.filter(name='customer').exists():
                return redirect('/customer/dashboard/')
            else:
                return redirect('/provider/dashboard/')
    
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
