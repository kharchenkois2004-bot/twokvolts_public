# consumers/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Consumer

class ConsumerRegistrationForm(UserCreationForm):
    """Расширенная форма регистрации с полями для Consumer"""
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=255, label='ФИО или название организации')
    type = forms.ChoiceField(choices=Consumer.USER_TYPE_CHOICES, label='Тип потребителя')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Адрес')
    phone = forms.CharField(max_length=20, label='Телефон')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                 'full_name', 'type', 'address', 'phone']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем классы Bootstrap к полям
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user