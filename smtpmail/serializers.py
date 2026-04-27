from rest_framework import serializers
from .models import SMTPConfig, EmailLog


class SMTPConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTPConfig
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = '__all__'
        read_only_fields = ['timestamp']   


        # Example: Ensure the body isn't empty
    def validate_body(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("The email body is too short!")
        return value 