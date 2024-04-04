import os
import random
import asyncio

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

import subprocess
import hmac
import hashlib
import json

from .messages import data_format_error
from .models import User, SafeAct, Take5
from .forms import LoginForm, RegisterForm, Take5Form, SafeActsForm, CorrectiveForm, UploadXLSForm
from .parser import validate_xls, get_workers_list, check_data_for_errors, counters
from .settings import MEDIA_ROOT


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
    return render(request, 'in_develop.html')


def safe_acts(request):
    return render(request, 'in_develop.html')


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
            return redirect('staff_status')
    else:
        form = UploadXLSForm()
    return render(request, 'upload_xls.html', {'form': form})


def staff_status(request):
    if validate_xls():
        df = get_workers_list()
        errors = check_data_for_errors(df)
        # errors = None
        if errors:
            for error in errors:
                messages.error(request, error)
        count_dict, row_dict = counters(df)
        row_dict = json.dumps(row_dict)
        dataset = df.to_dict(orient='records')
        return render(request, 'staff_status.html',
                      {'rows': dataset, 'count_dict': count_dict, 'row_dict': row_dict})
    else:
        messages.error(request, data_format_error)
        return redirect('upload_xls')


@csrf_exempt
async def webhook(request):
    signature_header = request.headers.get('x-hub-signature-256')
    # payload_body = request.body
    payload_body = await request.body()

    verify_signature(payload_body, os.getenv("GIT_WEBHOOK_TOKEN"), signature_header)

    # If the signature is verified, continue processing the webhook payload
    # Your webhook handling logic goes here
    asyncio.create_task(process_webhook_payload())

    return HttpResponse('Webhook received successfully!', status=200)


async def process_webhook_payload():
    # await asyncio.sleep(0)  # Эмуляция долгой операции
    subprocess.run(["/home/BartoGold/update_and_restart.sh"])


def verify_signature(payload, secret, signature):
    expected_signature = 'sha256=' + hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
    if signature != expected_signature:
        raise ValueError('Invalid signature')


TANK1 = [70, 'up', 90]
TANK2 = [50, 'down', 30]


@csrf_exempt  # Декоратор для обхода проверки CSRF (при необходимости)
def get_tanks_data(request):
    global TANK1, TANK2

    def tank_level(tank):
        if tank[1] == 'up':
            tank[0] += 3
            if tank[0] >= tank[2]:
                tank[1] = 'down'
                tank[2] = random.randint(30, 50)
        else:
            tank[0] -= 3
            if tank[0] <= tank[2]:
                tank[1] = 'up'
                tank[2] = random.randint(70, 90)
        return tank

    TANK1 = tank_level(TANK1)
    TANK2 = tank_level(TANK2)

    data = {
        'tank1': TANK1[0],
        'tank2': TANK2[0]
    }
    return JsonResponse(data)
