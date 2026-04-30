from django import forms
from .models import SMTPConfig

class EmailComposeForm(forms.Form):
    recipient = forms.EmailField(label="To")
    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea, label="Content")
    # This allows the user to pick which SMTP configuration to use
    smtp_server = forms.ModelChoiceField(
        queryset=SMTPConfig.objects.all(), 
        label="Send Via"
    )