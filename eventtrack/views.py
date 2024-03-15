from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from .messages import data_format_error
from .models import User, SafeAct, Take5
from .forms import LoginForm, RegisterForm, Take5Form, SafeActsForm, CorrectiveForm, UploadXLSForm
from .parser import validate_xls, get_workers_list, check_data_for_errors, counters
from django.contrib import messages
from .settings import MEDIA_ROOT

from django.shortcuts import render, redirect
from .forms import UploadXLSForm
from django.contrib.auth.decorators import login_required
import os

def index(request):
    return render(request, 'index.html')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Authenticate user and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                # Handle invalid login
                pass
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('index')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# def register(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             # Хешируем пароль
#             hashed_password = make_password(password)
#             # Создаем нового пользователя
#             user = User.objects.create_user(username=username, password=hashed_password)
#             # Сохраняем пользователя
#             user.save()
#             # Редирект на страницу входа или другую страницу
#             return redirect('login')
#     else:
#         form = RegisterForm()
#     return render(request, 'register.html', {'form': form})


def take5(request):
    return render(request, 'dashboard.html')


def safe_acts(request):
    return render(request, 'dashboard.html')


def upload_xls(request):
    if request.method == 'POST':
        form = UploadXLSForm(request.POST, request.FILES)
        if form.is_valid():
            breath_file = request.FILES['breath_list']
            evac_file = request.FILES['evac_list']

            breath_filename = 'breath.xlsx'
            evac_filename = 'evac.xlsx'

            destination_path = os.path.join(MEDIA_ROOT, breath_filename)
            with open(destination_path, 'wb+') as destination:
                for chunk in breath_file.chunks():
                    destination.write(chunk)

            destination_path = os.path.join(MEDIA_ROOT, evac_filename)
            with open(destination_path, 'wb+') as destination:
                for chunk in evac_file.chunks():
                    destination.write(chunk)

            # Далее обработка файлов и другие действия, которые вам нужны

            # После успешной загрузки файлов, перенаправляем на другую страницу
            return redirect('workers_status')
    else:
        form = UploadXLSForm()
    return render(request, 'upload_xls.html', {'form': form})


def workers_status(request):
    if validate_xls():
        df = get_workers_list()
        errors = check_data_for_errors(df)
        # errors = None
        if errors:
            for error in errors:
                messages.error(request, error)
        counter_msg = counters(df)
        dataset = df.to_dict(orient='records')
        return render(request, 'workers_status.html', {'rows': dataset, 'count_dict': counter_msg})
    else:
        messages.error(request, data_format_error)
        return redirect('upload_xls')

