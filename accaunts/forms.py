from django import forms
from accaunts.models import CustomUser


class UserEditName(forms.ModelForm):
    usname = forms.CharField(max_length=50, label='Сменить никнейм')

    class Meta:
        model = CustomUser
        fields = 'usname',

    # def clean_username(self):
    #     name = self.cleaned_data.get('username')
    #     CustomUser.objects.update(username=name)
