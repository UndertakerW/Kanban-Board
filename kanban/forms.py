from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from kanban.models import Profile, Task, Workspace


class OTPForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={
            'id': 'id_username',
            'class': "form-control",
        }
    ))
    otp = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={
            'id': 'otp',
            'class': "form-control",
        }
    ))


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
    username = forms.CharField(max_length=20,
                               widget=forms.TextInput(
                                   attrs={
                                       'id': 'id_username',
                                       'class': "form-control",
                                   }
                               ))
    password1 = forms.CharField(max_length=200,
                                label='Password',
                                widget=forms.PasswordInput(
                                    attrs={
                                        'id': 'id_password',
                                        'class': "form-control",
                                    }))
    password2 = forms.CharField(max_length=200,
                                label='Confirm password',
                                widget=forms.PasswordInput(
                                    attrs={
                                        'id': 'id_confirm_password',
                                        'class': "form-control",
                                    }))
    email = forms.CharField(max_length=50,
                            widget=forms.EmailInput(
                                attrs={
                                    'id': 'id_email',
                                    'class': "form-control",
                                }))
    first_name = forms.CharField(max_length=20,
                                 widget=forms.TextInput(
                                     attrs={
                                         'id': 'id_first_name',
                                         'class': "form-control",
                                     }
                                 ))
    last_name = forms.CharField(max_length=20,
                                widget=forms.TextInput(
                                    attrs={
                                        'id': 'id_last_name',
                                        'class': "form-control",
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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['participants'].queryset = User.objects.exclude(id=user.id)

    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'participants-checkbox'}),
        required=False,
    )

    color_scheme_choices = [
        (1, 'Light'),
        (2, 'Dark')
        # Add more color schemes if needed
    ]
    color_scheme = forms.ChoiceField(
        choices=color_scheme_choices,
        widget=forms.Select(attrs={'class': 'color-scheme-select'}),
    )

    class Meta:
        model = Workspace
        fields = ['name', 'participants', 'color_scheme']
        widgets = {
            'name': forms.TextInput(attrs={'id': 'id_name_input_text'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

        STATUS_CHOICES = (
            (1, 'To do'),
            (2, 'In progress'),
            (3, 'Done'),
        )

        PRIORITY_CHOICES = (
            (1, 'High'),
            (2, 'Medium'),
            (3, 'Low'),
        )

        widgets = {
            'taskname': forms.TextInput(attrs={'id': 'id_taskname_input_text'}),
            'description': forms.TextInput(attrs={'id': 'id_description_input_text'}),
            #'assignee': forms.Select(attrs={'id': 'id_assignee_input_select'}, choices=User.objects.filter(is_active=True)),
            'creation_date': forms.DateInput(attrs={'id': 'id_creation_date_input_date'}),
            'due_date': forms.DateInput(attrs={'id': 'id_due_date_input_date'}),
            'status': forms.Select(choices=STATUS_CHOICES, attrs={'id': 'id_status_input_select'}),
            'priority': forms.Select(choices=PRIORITY_CHOICES, attrs={'id': 'id_priority_input_select'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_description']

        widgets = {
            'profile_description': forms.TextInput(attrs={'id': 'id_profile_description_text'})
        }
