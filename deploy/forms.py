from django import forms
from .models import GitProject
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
            'repository_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/usuario/repositorio',
                'id': 'id_repository_url'
            }),
            'webhook_secret': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Gerado automaticamente ou insira manualmente',
                'id': 'id_webhook_secret'
            }),
        }

    def clean_webhook_secret(self):
        webhook_secret = self.cleaned_data.get('webhook_secret')
        if not webhook_secret:
            webhook_secret = secrets.token_hex(32)
        return webhook_secret