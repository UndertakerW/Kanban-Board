from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from kanban.models import Profile, Task


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(
            attrs={
                'id': 'id_username',
            }
        ))
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(
            attrs={
                    'id': 'id_password',
                }
        ))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


class RegisterForm(forms.ModelForm):

    class Meta:
        model = Profile
        exclude = ['register_type', 'authentication_status']
        widgets = {'password': forms.PasswordInput(), 'confirm_password': forms.PasswordInput()}

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

