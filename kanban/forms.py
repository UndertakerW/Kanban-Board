from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from kanban.models import Registration, Task


class LoginForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['username', 'password']
        widgets = {'password': forms.PasswordInput()}

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        return cleaned_data


class RegisterForm(forms.ModelForm):

    class Meta:
        model = Registration
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

