from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RoomCleaningForm


# @login_required
def roomcleaning(request):
    if not messages.get_messages(request):
        messages.success(request, 'Select a room:')
    return render(request, 'roomcleaning.html')  #, {'form': form, 'grouped_fields': grouped_fields})


# @login_required
def roomcleaning_add(request):
    time_start = timezone.now
    if request.method == 'POST':
        form = RoomCleaningForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            for f in files:
                pass
            print(form.data)
            messages.success(request, 'Thank you, great job!')
            return redirect('roomcleaning')
        else:
            print(form.errors)
    else:
        form = RoomCleaningForm()

    grouped_fields = {}
    for field in form.visible_fields():
        if field.name.startswith('question'):
            group_name = field.help_text
            if group_name not in grouped_fields:
                grouped_fields[group_name] = []
            grouped_fields[group_name].append(field)

    return render(request, 'roomcleaning_add.html', {'form': form, 'grouped_fields': grouped_fields})


def survey_add(request):
    return render(request, 'survey_add.html')
