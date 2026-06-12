import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Имейл",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Имейл")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Неверный имейл или пароль")
        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return None
        phone = phone.strip().replace(" ", "").replace("-", "")
        if re.fullmatch(r"8\d{10}", phone):
            phone = "+7" + phone[1:]
        elif not re.fullmatch(r"\+7\d{10}", phone):
            raise forms.ValidationError(
                "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            )
        queryset = User.objects.filter(phone=phone)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Пользователь с таким номером телефона уже существует")
        return phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        return validate_github_url(github_url)


class TeamFinderPasswordChangeForm(PasswordChangeForm):
    pass


def validate_github_url(value):
    if not value:
        return ""
    host = urlparse(value).netloc.lower()
    if host not in ("github.com", "www.github.com"):
        raise forms.ValidationError("Ссылка должна вести на GitHub")
    return value
