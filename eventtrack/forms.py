from django import forms

YES_NO_NA_CHOICES = [(2, 'Not app'), (1, 'YES'), (0, 'NO')]
HAZARDS_CHOICES = [(1, 'Notice'), (2, 'Low'), (3, 'Medium'), (4, 'High'), (5, 'Extream')]
Q_TEXT = "Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?"


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput(), min_length=4, max_length=20)


class SafeActsForm(forms.Form):
    location = forms.CharField(label='Description', max_length=250)
    q1 = forms.ChoiceField(label=f'1. {Q_TEXT}', choices=YES_NO_NA_CHOICES)
    q2 = forms.ChoiceField(label=f'2. {Q_TEXT}', choices=YES_NO_NA_CHOICES)
    q3 = forms.ChoiceField(label=f'3. {Q_TEXT}', choices=YES_NO_NA_CHOICES)
    q4 = forms.ChoiceField(label=f'4. {Q_TEXT}', choices=YES_NO_NA_CHOICES)
    q5 = forms.ChoiceField(label=f'5. {Q_TEXT}', choices=YES_NO_NA_CHOICES)


class Take5Form(forms.Form):
    hazard = forms.ChoiceField(label='Hazard level', choices=HAZARDS_CHOICES)
    description = forms.CharField(label='Description', max_length=250)
    qA = forms.ChoiceField(label=f'A. {Q_TEXT}', choices=YES_NO_NA_CHOICES)
    qB = forms.ChoiceField(label=f'B. {Q_TEXT}', choices=YES_NO_NA_CHOICES)
    qC = forms.ChoiceField(label=f'C. {Q_TEXT}', choices=YES_NO_NA_CHOICES)
    qD = forms.ChoiceField(label=f'D. {Q_TEXT}', choices=YES_NO_NA_CHOICES)
    qE = forms.ChoiceField(label=f'E. {Q_TEXT}', choices=YES_NO_NA_CHOICES)
    qF = forms.ChoiceField(label=f'F. {Q_TEXT}', choices=YES_NO_NA_CHOICES)


class CorrectiveForm(forms.Form):
    location = forms.CharField(label='Location', max_length=100)
    action = forms.CharField(label='Required action', max_length=250)
    act_by = forms.CharField(label='Action by', max_length=100)
    act_date = forms.DateField(label='Due date')


class UploadXLSForm(forms.Form):
    breath_list = forms.FileField(label='1. Breathalyser activity report',
                                  widget=forms.ClearableFileInput(
                                      attrs={
                                          'accept': '.xls, .xlsx',
                                          'style': 'font-size: 16px; color: #00428a; width: 500px; height: 30px;'}))
    evac_list = forms.FileField(label='2. Evacuation list',
                                widget=forms.ClearableFileInput(
                                    attrs={
                                        'accept': '.xls, .xlsx',
                                        'style': 'font-size: 16px; color: #00428a; width: 500px; height: 30px;'}))
