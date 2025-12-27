from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Consumer
from .forms import ConsumerRegistrationForm

class ConsumerRegisterView(CreateView):
    """Регистрация нового потребителя"""
    form_class = ConsumerRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Создаем профиль Consumer для нового пользователя
        Consumer.objects.create(
            user=self.object,
            full_name=form.cleaned_data['full_name'],
            type=form.cleaned_data['type'],
            address=form.cleaned_data['address'],
            phone=form.cleaned_data['phone']
        )
        # Автоматически логиним пользователя после регистрации
        login(self.request, self.object)
        return response