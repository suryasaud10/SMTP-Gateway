import base64
from celery import shared_task
from django.core.mail import get_connection, EmailMultiAlternatives

@shared_task
def send_email_queue(subject, message, fromEmail, recipientList, emailHostId, attachments=None, log_id=None):
    from .models import EmailHost, EmailLog  # Import here to avoid circular imports
    
    try:
        # --- YOUR ORIGINAL CODE START ---
        try:
            emailHost = EmailHost.objects.get(pk=emailHostId, isDeleted=False)
        except EmailHost.DoesNotExist:
            if log_id:
                EmailLog.objects.filter(pk=log_id).update(status='FAILED', error_message="Host ID not found")
            return

        # Choose SSL or TLS based on your logic
        if emailHost.security == "TLS":
            connection = get_connection(
                host=emailHost.smtpHost,
                port=emailHost.smtpPort,
                username=emailHost.smtpUser,
                password=emailHost.smtpPassword,
                use_tls=True,
            )
        elif emailHost.security == "SSL":
            connection = get_connection(
                host=emailHost.smtpHost,
                port=emailHost.smtpPort,
                username=emailHost.smtpUser,
                password=emailHost.smtpPassword,
                use_ssl=True,
            )
        
        email = EmailMultiAlternatives(
            subject=subject + "\u200b",
            body=message,
            from_email=fromEmail or emailHost.smtpUser,
            to=recipientList,
            connection=connection,
        )
        email.content_subtype = "html"

        if attachments:
            for att in attachments:
                file_name = att["name"]
                file_content = base64.b64decode(att["content"])
                mime_type = att.get("type", "application/octet-stream")
                email.attach(file_name, file_content, mime_type)

        email.send() # The actual "Real" sending process
        # --- YOUR ORIGINAL CODE END ---

        # Update log to SENT
        if log_id:
            EmailLog.objects.filter(pk=log_id).update(status='SENT')

    except Exception as e:
        if log_id:
            EmailLog.objects.filter(pk=log_id).update(status='FAILED', error_message=str(e))