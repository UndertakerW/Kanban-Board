from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from kanban.models import Profile, Task, Workspace


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


class RegisterForm(forms.Form):

    username   = forms.CharField(max_length=20, widget=forms.TextInput(
            attrs={
                'id': 'id_username',
            }
        ))
    password1  = forms.CharField(max_length=200,
                                 label='Password', 
                                 widget=forms.PasswordInput(
            attrs={
                    'id': 'id_password',
            }))
    password2  = forms.CharField(max_length=200,
                                 label='Confirm password',  
                                 widget=forms.PasswordInput(
            attrs={
                    'id': 'id_confirm_password',
            }))
    email      = forms.CharField(max_length=50,
                                 widget = forms.EmailInput(
            attrs={
                    'id': 'id_email',
            }))
    first_name = forms.CharField(max_length=20, widget=forms.TextInput(
            attrs={
                'id': 'id_first_name',
            }
        ))
    last_name  = forms.CharField(max_length=20, widget=forms.TextInput(
            attrs={
                'id': 'id_last_name',
            }
        ))
    

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

class NewWorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ['name', 'participants', 'color_scheme']
        widgets = {
            'name': forms.TextInput(attrs={'id': 'id_name_input_text'}),
            # TODO: User can specify zero or more participants by email
            # TODO: User can select a color scheme
        }

