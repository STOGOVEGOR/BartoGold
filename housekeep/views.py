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
    if request.method == 'POST':
        if request.POST.get('feedback'):
            messages.success(request, 'Thanks for your feedback!')
            return redirect('survey_add')
        if not request.POST.get('rating'):
            messages.success(request, 'Please select one of the emoticons!')
            return redirect('survey_add')
        rating = request.POST.get('rating')
        if int(rating) == 5:
            messages.success(request, 'Will be glad to see you again!')
        elif 4 >= int(rating) >= 2:
            messages.success(request, 'We will try to improve our service!')
        else:
            messages.success(request, 'We are really sorry, tell us more about your experience please:')
            return render(request, 'survey_add.html', {'feedback': True})
        return redirect('survey_add')
    return render(request, 'survey_add.html')
