from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Event, Club, ClubMembership, EventRegistration

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field].label
            })

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio', 'department')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Tell us about yourself...'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your department'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ClubUpdateForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'category', 'image', 'thumbnail']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'capacity', 'registration_deadline', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = []  # We'll handle the fields in the view

class ClubMembershipForm(forms.ModelForm):
    class Meta:
        model = ClubMembership
        fields = []  # We'll handle the fields in the view

class LeaderAssignmentForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        empty_label="Select a member",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, club, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show approved members who aren't already leaders
        self.fields['user'].queryset = User.objects.filter(
            clubmembership__club=club,
            clubmembership__status='approved'
        ).exclude(
            clubmembership__role__in=['leader', 'faculty_advisor']
        )
