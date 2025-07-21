from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from news.models import UserPreference, Category  # <-- Add this import


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserPreferenceForm(forms.ModelForm):
    preferred_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserPreference
        fields = ['preferred_categories']