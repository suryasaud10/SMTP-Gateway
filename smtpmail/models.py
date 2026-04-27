from django.db import models

# Create your models here.

class SMTPConfig(models.Model):
    host = models.CharField(max_length=255, default='smtp.example.com')
    port = models.IntegerField(default=587)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)

    class Meta:
        verbose_name = "SMTP Configuration"
        verbose_name_plural = "SMTP Configurations"

    def __str__(self):
        return f"{self.username}:{self.host}"
    

class EmailLog(models.Model):
    sender_email = models.EmailField()
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email from {self.sender_email} to {self.recipient_email} at {self.timestamp}"