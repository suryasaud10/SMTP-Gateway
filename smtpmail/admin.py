from django.contrib import admin

# Register your models here.
from .models import SMTPConfig, EmailLog

@admin.register(SMTPConfig)
class SMTPConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'port', 'username')
    readonly_fields = ('id',)
    # search_fields = ('host', 'username')

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('sender_email', 'recipient_email', 'subject', 'timestamp')
    #Keep timestamp read-only in admin
    readonly_fields = ('timestamp',)