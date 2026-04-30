import base64
from celery import shared_task
from django.core.mail import get_connection, EmailMultiAlternatives


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def send_email_queue(self, subject, message, fromEmail, recipientList, emailHostId, attachments=None, log_id=None):
    from .models import SMTPConfig, EmailLog  
    
    try:
        try:
            emailHost = SMTPConfig.objects.get(pk=emailHostId)
        except SMTPConfig.DoesNotExist:
            if log_id:
                EmailLog.objects.filter(pk=log_id).update(status='FAILED', error_message="Host ID not found")
            return "FAILED: Host ID not found"

        # --- ensure recipients is list ---
        if isinstance(recipientList, str):
            recipientList = [r.strip() for r in recipientList.split(",") if r.strip()]

        if not recipientList:
            if log_id:
                EmailLog.objects.filter(pk=log_id).update(status="FAILED", error_message="Empty recipient list")
            return "FAILED: no recipients"


        print(f"DEBUG: Connecting to {emailHost.host}:{emailHost.port} as {emailHost.username}")

        # --- FIX: Match your model fields (host, port, username, password, use_tls) ---
        # Django's get_connection is smart enough to use TLS/SSL if the booleans are passed
        connection = get_connection(
            host=emailHost.host, 
            port=emailHost.port, 
            username=emailHost.username, 
            password=emailHost.password, 
            use_tls=emailHost.use_tls,
            use_ssl=getattr(emailHost, 'use_ssl', False), # use_ssl only if you added it to models
        )

         # --- FORCE CONNECTION TEST ---
        try:
            connection.open()
            print("DEBUG: Connection opened successfully!")
        except Exception as e:
            print(f"DEBUG: Connection failed: {e}")
            raise e # This will trigger the retry or show the error in logs

        # --- build email ---
        email = EmailMultiAlternatives(
            subject=subject + "\u200b",
            body=message,
            from_email=fromEmail or emailHost.username, # Use 'username' not 'smtpUser'
            to=recipientList,
            connection=connection,
        )

        email.content_subtype = "html"

        if attachments:
            for att in attachments:
                try:
                    file_name = att["name"]
                    file_content = base64.b64decode(att["content"])
                    mime_type = att.get("type", "application/octet-stream")
                    email.attach(file_name, file_content, mime_type)
                except Exception as att_err:
                    if log_id:
                        EmailLog.objects.filter(pk=log_id).update(error_message=f"Attachment error: {str(att_err)}")
                    return f"FAILED: attachment error - {str(att_err)}"
                
        email.send()

        # Update log to SENT
        if log_id:
            EmailLog.objects.filter(pk=log_id).update(status='SENT')
        return "SENT"

    except Exception as e:
        if log_id:
            EmailLog.objects.filter(pk=log_id).update(status='FAILED', error_message=str(e))
        return f"FAILED: {str(e)}"