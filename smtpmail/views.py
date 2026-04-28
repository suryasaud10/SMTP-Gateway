from urllib import request

from django.shortcuts import render
from rest_framework import viewsets, status
from .models import SMTPConfig, EmailLog
from .serializers import SMTPConfigSerializer, EmailLogSerializer
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMessage, get_connection

# Create your views here.


class SMTPViewset(viewsets.ModelViewSet):
        queryset = SMTPConfig.objects.all()
        serializer_class = SMTPConfigSerializer
    

        @action(detail=True, methods=['post'])
        @permission_classes([AllowAny])  # Allow anyone to send emails using this endpoint
        # Now get_object() will work because 'pk' (the ID) is in the URL
        def send_email(self, request, pk=None):
            config = self.get_object()

            # Pull data from the request body
            subject = request.data.get('subject', 'Test Email')
            body = request.data.get('body', 'This is a test.')
            recipients = request.data.get('recipients', []) # Should be a list

            # Ensure recipients is a list
            if isinstance(recipients, str):
                recipients = [recipients]

            if not recipients:
                return Response({'error': 'No recipients provided'}, status=status.HTTP_400_BAD_REQUEST)

            try:
            # 1. Setup Connection
                connection = get_connection(
                    host=config.host,
                    port=config.port,
                    username=config.username,
                    password=config.password,
                    use_tls=config.use_tls
            )

            # 2. Send Email
                email = EmailMessage(
                        subject = subject,
                        body = body,
                        from_email = config.username,
                        to = recipients,
                        connection = connection
                )
                email.send()

            # 3. Log the success
                EmailLog.objects.create(
                    sender_email=config.username,
                    recipient_emails=", ".join(recipients),
                    subject=subject,
                    body=body
                )

                return Response({'status': 'Email sent!'}, status=status.HTTP_200_OK)
            except Exception as e:
                # Log the actual error for debugging
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)