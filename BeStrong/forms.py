from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm


class UserRegistrationForm(UserCreationForm):
    last_name = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nume'})
    )
    first_name = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prenume'})
    )
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label="",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone = forms.RegexField(
        regex=r'^\d{10}$',
        error_messages={'invalid': "Numărul de telefon trebuie să conțină 10 cifre."},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Număr de telefon'}),
        label='',
   )

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.label = ''
            field.help_text = ''
            if not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = field_name.replace('_', ' ').capitalize()

        self.fields['password1'].widget.attrs['placeholder'] = 'Parolă'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmă parola'

class ClientTrainerSelectForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['trainer']
        widgets = {
            'trainer': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'trainer': ''
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trainer'].queryset = UserProfile.objects.filter(role='trainer', is_approved=True)

class ReassignTrainerForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['trainer']
        widgets = {
            'trainer': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trainer'].queryset = UserProfile.objects.filter(role='trainer', is_approved=True)