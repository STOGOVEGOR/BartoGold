from django import forms
from multiupload.fields import MultiFileField

ROOM_CHOICES = [
    ('11', 'Room 11'),
    ('12', 'Room 12'),
    ('14', 'Room 14'),
    ('24', 'Room 24'),
    ('25', 'Room 25'),
]

MAINTENANCE_CHOICES = [
    (1, 'No need any maintenance'),
    (2, 'Need a preventive maintenance'),
    (3, 'Need a corrective maintenance'),
    (4, 'Need a major maintenance'),
]

ANSWERS = (('YES', 'YES'), ('NO', 'NO'))
# ROOM_QUESTIONS = [
#     'No Damage',
#     'No Excess',
# ]
ROOM_QUESTIONS = {
    'Condition': ['No Damage', 'No Excess', 'No Rubbish', 'No Dirt'],
    'Textile': ['2 Pillows', 'Mattress Protector', 'Fitted Sheet', 'Flat Sheet',
                'Doona', 'Doona cover', '2 Towels', 'Bath Matt'],
    'Bathroom': ['Shower Clean', 'No Mold', 'No Used Soap Bars', 'Toilet Cleaned',
                 'Toilet Paper 2pcs', '2 Sachets Of Laundry Powder', 'All Linen And Towels Are Replaced'],
    'Electronics': ['TV Checked', 'TV Remote Control', 'AC Checked', 'AC Remote Control', 'Fridge Working',
                    'Fridge Clean'],
    'Cleaning': ['Emptied bin and replace with new liner', 'Swept and mopped all floors'],
    'Documents': ['Evacuation Poster', 'Camp Contacts', 'Maintenance', 'Feedback QR Codes', 'Night Shift Sticker'],
}


class RoomCleaningForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(RoomCleaningForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''

    room = forms.ChoiceField(choices=ROOM_CHOICES, label='Room')
    maintenance = forms.ChoiceField(choices=MAINTENANCE_CHOICES, label='Maintenance')
    for idx, (category, questions) in enumerate(ROOM_QUESTIONS.items(), start=1):
        for jdx, question in enumerate(questions, start=1):
            field_name = f'question{idx}_{jdx}'
            locals()[field_name] = forms.ChoiceField(
                label=question,
                choices=ANSWERS,
                help_text=category,
                initial="YES",
            )
    # for idx, label in enumerate(ROOM_QUESTIONS, start=1):
    #     field_name = f'question{idx}'
    #     locals()[field_name] = forms.ChoiceField(
    #         label=label,
    #         choices=ANSWERS,
    #         initial="YES",
    #     )
    # question1_1 = forms.ChoiceField(
    #     label='No Damage',
    #     choices=ANSWERS,
    #     initial="YES",
    # )
    comment = forms.CharField(label='Note', max_length=250, required=False,
                              widget=forms.Textarea(
                                  attrs={'placeholder': 'Type your comments here',
                                         'style': 'font-size: 16px;',
                                         'rows': 4, 'cols': 42}))
    files = MultiFileField(min_num=1, max_num=10, max_file_size=1024 * 1024 * 5, required=False)
    # files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
