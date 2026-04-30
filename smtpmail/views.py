from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import SMTPConfig, EmailLog
from .serializers import SMTPConfigSerializer
from .tasks import send_email_queue
from .forms import EmailComposeForm

# 1. API ViewSet for programmatic email sending
class SMTPViewset(viewsets.ModelViewSet):
    queryset = SMTPConfig.objects.all()
    serializer_class = SMTPConfigSerializer

    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        config = self.get_object()
        subject = request.data.get('subject', 'Test Email')
        body = request.data.get('body', 'This is a test.')
        recipients = request.data.get('recipients')
        
        # Handle recipients as string or list
        if isinstance(recipients, str):
            recipients = [r.strip() for r in recipients.split(',') if r.strip()]
        
        if not recipients:
            return Response({'error': 'No recipients provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Create log entry within the transaction
        log = EmailLog.objects.create(
            smtp_config=config,
            sender_email=config.username,
            recipient_email=", ".join(recipients),
            subject=subject,
            body=body,
            status='QUEUED'
        )       

        # Use transaction.on_commit to delay task until DB write is finished
        transaction.on_commit(lambda: send_email_queue.delay(
            subject=subject,
            message=body,
            fromEmail=config.username,
            recipientList=recipients,
            emailHostId=config.id,
            log_id=log.id
        ))
        
        return Response({
            "status": "queued",
            "log_id": log.id,
            "message": "Email sent to queue"
        }, status=status.HTTP_202_ACCEPTED)

# ui part
class SendEmailView(FormView):
    template_name = 'smtpmail/send_email.html'
    form_class = EmailComposeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = get_object_or_404(SMTPConfig, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        config = get_object_or_404(SMTPConfig, pk=self.kwargs['pk'])
        recipient = form.cleaned_data['recipient']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        
        # We use a transaction to ensure the log is saved before the task runs
        with transaction.atomic():
            log = EmailLog.objects.create(
                smtp_config=config,
                sender_email=config.username,
                recipient_email=recipient,
                subject=subject,
                body=message,
                status='QUEUED'
            )

            # Trigger Celery (The background version of your shell command)
            transaction.on_commit(lambda: send_email_queue.delay(
                subject=subject,
                message=message,
                fromEmail=config.username,
                recipientList=[recipient],
                emailHostId=config.id,
                log_id=log.id
            ))
        
        messages.success(self.request, f"Success! Email for {recipient} is now in the queue.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('email_form_class', kwargs={'pk': self.kwargs['pk']})