"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses bootstrap CSS."""
    username = forms.CharField(max_length=30,
                               widget=forms.TextInput({
                                   'placeholder': 'Username'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'placeholder': 'Password'}))


class SignupForm(UserCreationForm):
    """Signup form which uses bootstrap CSS."""
    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                    "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")},
        widget=forms.TextInput({
            'class': 'form-control', 'placeholder': 'Username',
            'required': 'true'}))
    email = forms.EmailField(
        widget=forms.TextInput({
            'class': 'form-control', 'placeholder': 'Email',
            'required': 'true'}))
    password1 = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput({
            'class': 'form-control', 'placeholder': 'Password',
            'required': 'true'}))
    password2 = forms.CharField(
        label=_("Password confirmation"), widget=forms.PasswordInput({
            'class': 'form-control', 'placeholder': 'Password confirmation',
            'required': 'true'}),
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ('username', 'email')


class UploadForm(forms.Form):
    image = forms.ImageField(label="Select image")