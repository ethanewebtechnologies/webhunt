from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from parsley.decorators import parsleyfy

@parsleyfy
class UploadFileForm(forms.Form):
    contact_file = forms.FileField()

@parsleyfy
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(min_length=3, max_length=30, required=True, help_text='Required. Provide a valide name.')
    last_name = forms.CharField(min_length=3, max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        parsley_namespace = 'parsley'
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
