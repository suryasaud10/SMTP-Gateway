from rest_framework import viewsets, status
from .models import SMTPConfig, EmailLog
from .serializers import SMTPConfigSerializer, EmailLogSerializer
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from .tasks import send_email_queue
from django.shortcuts import render, get_object_or_404

# Create your views here.

class SMTPViewset(viewsets.ModelViewSet):
    queryset = SMTPConfig.objects.all()
    serializer_class = SMTPConfigSerializer

    @action(detail=True, methods=['get', 'post'], serializer_class=EmailLogSerializer)
    @permission_classes([AllowAny])
    def send_email(self, request, pk=None):
        # 1. Fetch config first so GET requests can at least see it's a valid ID
        config = self.get_object()

        # 2. Only run the send logic on POST
        if request.method == 'POST':
            subject = request.data.get('subject', 'Test Email')
            body = request.data.get('body', 'This is a test.')
            attachments = request.data.get('attachments', None)
            recipients = request.data.get('recipients') or request.data.get('recipient_email')  # Support both 'recipients' and 'recipient' keys

            # Convert to list if it's a string (from form or comma-separated)
            if isinstance(recipients, str):
                recipients = [r.strip() for r in recipients.split(',') if r.strip()]
            elif isinstance(recipients, list):
                recipients = recipients
            else:
                recipients = []

            if not recipients:
                return Response({'error': 'No recipients provided'}, status=status.HTTP_400_BAD_REQUEST)

            # 3. Create the log entry
            log = EmailLog.objects.create(
                smtp_config_id=config.id,  # Store the ID of the SMTPConfig used
                sender_email=config.username,
                recipient_email=", ".join(recipients), 
                subject=subject,
                body=body,
                status='QUEUED'
            )

            # 4. Enqueue the task
            send_email_queue.delay(
                log_id=log.id, 
                smtp_config_id=config.id, 
                recipients=recipients, 
                subject=subject, 
                body=body,
                attachments=attachments
            )

            return Response({
                "status": "queued",
                "log_id": log.id,
                "message": f"Task sent to celery for {len(recipients)} recipient(s)"   
            }, status=status.HTTP_202_ACCEPTED)

        # 3. If request is GET, show a friendly instruction instead of an error
        return Response({
            "message": "Fill the form to send an email.",
            "config_found": config.username
        })

def email_form_view(request, pk):
    # This just ensures the SMTP config exists before showing the form
    config = get_object_or_404(SMTPConfig, pk=pk)
    return render(request, 'smtpmail/send_email.html', {'config_id': pk, 'config': config})