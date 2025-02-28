from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from .models import AnimeReview

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'profile_image', 'bio']

class AnimeReviewForm(forms.ModelForm):
    class Meta:
        model = AnimeReview
        fields = ['review_text', 'recommendation']
        widgets = {
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts about this anime...',
                'rows': 4
            }),
            'recommendation': forms.Select(attrs={'class': 'form-control'})
        }
