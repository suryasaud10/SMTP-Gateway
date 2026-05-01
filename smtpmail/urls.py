from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter
from smtpmail.views import SMTPViewset

router = DefaultRouter()

# This creates /smtp/, /smtp/1/, and /smtp/1/send_email/ automatically
router.register(r'smtp', views.SMTPViewset, basename='smtp')

urlpatterns = [
    path('api/', include(router.urls)),
    path('send-form/<int:pk>/', views.SMTPViewset.as_view(
        {'post': 'send_email'}
    ), name='SendEmailView'),
]