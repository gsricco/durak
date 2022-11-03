from django import forms
from accaunts.models import CustomUser


class UserEditName(forms.ModelForm):
    username = forms.CharField(max_length=20,) # widget=forms.TextInput(
        # attrs={'class': "form__input form profile-settings__name", 'type': "text", }))

    class Meta:
        model = CustomUser
        fields = 'username',
