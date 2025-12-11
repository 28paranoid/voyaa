from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Event, Branding, MatchRegistration

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'start_time', 'location']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class BrandingForm(forms.ModelForm):
    class Meta:
        model = Branding
        fields = ['logo', 'primary_color', 'registration_open']
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
        }
        labels = {
            'registration_open': 'Team Registration Open',
        }

class MatchRegistrationForm(forms.ModelForm):
    class Meta:
        model = MatchRegistration
        fields = ['team_name', 'discord_id', 'members']
        widgets = {
            'members': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter team member names, separated by commas'}),
        }
        labels = {
            'team_name': 'Team Name',
            'discord_id': 'Discord ID',
            'members': 'Team Members',
        }
