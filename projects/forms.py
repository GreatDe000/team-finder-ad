from django import forms

from users.utils import validate_github_url

from .models import Project

PROJECT_DESCRIPTION_ROWS = 6


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = (("open", "Открыт"), ("closed", "Закрыт"))

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": PROJECT_DESCRIPTION_ROWS}),
        }

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url"))
