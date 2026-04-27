from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# This creates /smtp/, /smtp/1/, and /smtp/1/send_email/ automatically
router.register(r'smtp', views.SMTPViewset, basename='smtp')

urlpatterns = [
    path('api/', include(router.urls)),
]