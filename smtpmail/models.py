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
    STATUS_CHOICES = [
        ('QUEUE', 'Queued'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]
     # Store the ID of the SMTPConfig used for this email
    smtp_config_id = models.PositiveBigIntegerField(help_text="ID of the SMTP configuration used for this email") 

    sender_email = models.EmailField()
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()

    # this field will automatically set the timestamp when a new log entry is created
    timestamp = models.DateTimeField(auto_now_add=True)

    # status to track if the email is queued, sent, or failed
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='QUEUE')

    error_message = models.TextField(blank=True, null=True, help_text="Store error message if email sending fails")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Email from {self.sender_email} to {self.recipient_email} at {self.timestamp}"
    sender_email = models.EmailField()
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()

    # this field will automatically set the timestamp when a new log entry is created
    timestamp = models.DateTimeField(auto_now_add=True)

    # status to track if the email is queued, sent, or failed
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='QUEUE')

    error_message = models.TextField(blank=True, null=True, help_text="Store error message if email sending fails")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Email from {self.sender_email} to {self.recipient_email} at {self.timestamp}"