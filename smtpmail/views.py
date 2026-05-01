from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import SMTPConfig, EmailLog
from .serializers import SMTPConfigSerializer, EmailLogSerializer
from .tasks import send_email_queue
from django.shortcuts import render

class EmailSendSerializer(serializers.Serializer):
    """This defines exactly what the form should show in the browser."""
    subject = serializers.CharField(max_length=255, required=True)
    message = serializers.CharField(required=True)
    recipient = serializers.CharField(help_text="Enter emails separated by commas", required=True)

class SMTPViewset(viewsets.ModelViewSet):
    queryset = SMTPConfig.objects.all()
    serializer_class = SMTPConfigSerializer

    def get_serializer_class(self):
        # This tells DRF to show the Email form when on the 'send-form' page
        if self.action == 'send_email':
            return EmailSendSerializer
        return SMTPConfigSerializer

    @action(detail=True, methods=['post'], url_path='send-form')
    def send_email(self, request, pk=None):
        config = self.get_object()
        
        # Use the serializer to handle the data instead of manual request.data.get
        serializer = EmailSendSerializer(data=request.data)
        
        if serializer.is_valid():
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']
            recipients_raw = serializer.validated_data['recipient']
            
            # Convert string to list
            recipients = [r.strip() for r in recipients_raw.split(',') if r.strip()]

            # Create the log
            log = EmailLog.objects.create(
                smtp_config_id=config.id,
                sender_email=config.username,
                recipient_email=", ".join(recipients),
                subject=subject,
                body=message,
                status='QUEUED'
            )

            transaction.on_commit(lambda: send_email_queue.delay(
                subject=subject,
                message=message,
                fromEmail=config.username,
                recipientList=recipients,
                emailHostId=config.id,
                log_id=log.id
            ))

            return render(request, "smtpmail/email_form_success.html")  # Redirect to a success page after queuing the email
        else:
                
        # If the form is missing data, DRF will show exactly which field is empty
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)