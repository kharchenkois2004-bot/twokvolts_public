from django.urls import path
from . import views

from django.views.generic import TemplateView

app_name = 'billing'

urlpatterns = [
    path('', TemplateView.as_view(template_name='list.html'), name='list'),
]