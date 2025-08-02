from django import forms
from .models import GitProject
import re
import secrets

class GitProjectForm(forms.ModelForm):
    class Meta:
        model = GitProject
        fields = ['name', 'repository_url', 'webhook_secret']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: meu-projeto-api',
                'id': 'id_name'
            }),
            'repository_url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: git@github.com:user/repo.git ou https://github.com/user/repo.git',
                'id': 'id_repository_url'
            }),
            'webhook_secret': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Gerado automaticamente ou insira manualmente',
                'id': 'id_webhook_secret'
            }),
        }

    def clean_repository_url(self):
        url = self.cleaned_data['repository_url']
        ssh_pattern = r'^git@[\w\.]+:[\w\-]+/[\w\-]+(\.git)?$'
        https_pattern = r'^https://[\w\.]+/[\w\-]+/[\w\-]+(\.git)?$'
        if not re.match(ssh_pattern, url) and not re.match(https_pattern, url):
            raise forms.ValidationError("Informe uma URL válida SSH ou HTTPS.")
        return url

    def clean_webhook_secret(self):
        token = self.cleaned_data.get('webhook_secret')
        if not token:
            token = secrets.token_hex(32)
        return token
