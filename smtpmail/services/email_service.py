import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.cache import cache


def get_smtp_connection(config):
    """Establish an smtp connection using the provided configuration.
    supports both ssl and starttls based on the config.
    """

    if get_smtp_connection(config):
        server = smtplib.SMTP_SSL(config.host, config.port, timeout= 30)

    else:
        server = smtplib.SMTP(config.host, config.port, timeout= 30)
        if config.use_tls:
            server.starttls()

    server.login(config.username, config.password)
    return server   

def send_email_via_smtp(config, subject, body, recipients):
    """Send an email using the provided configuration and email details.
    This function will be called by the Celery task to send emails asynchronously.
    """

    try:
        server = get_smtp_connection(config)

        msg = MIMEMultipart()
        msg['From'] = config.username
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Add HTML support here if body contains HTML tags
        server.sendmail(config.username, recipients, msg.as_string())
    finally:
        if server:
            server.quit()