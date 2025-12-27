# meter_readings/forms.py
from django import forms
from django.utils import timezone
from .models import MeterReading
from contracts.models import Contract

class MeterReadingForm(forms.ModelForm):
    class Meta:
        model = MeterReading
        fields = ['contract', 'reading_date', 'value']
        widgets = {
            'reading_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'max': timezone.now().date().strftime('%Y-%m-%d')
                }
            ),
            'value': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.001',
                    'min': '0'
                }
            ),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Ограничиваем выбор только активными договорами пользователя
            from consumers.models import Consumer
            try:
                consumer = Consumer.objects.get(user=self.user)
                self.fields['contract'].queryset = Contract.objects.filter(
                    consumer=consumer,
                    is_active=True
                )
            except Consumer.DoesNotExist:
                self.fields['contract'].queryset = Contract.objects.none()
        
        self.fields['contract'].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        contract = cleaned_data.get('contract')
        value = cleaned_data.get('value')
        reading_date = cleaned_data.get('reading_date')
        
        if contract and value and reading_date:
            # Проверяем, чтобы новые показания были больше предыдущих
            previous = MeterReading.objects.filter(
                contract=contract,
                reading_date__lt=reading_date
            ).order_by('-reading_date').first()
            
            if previous and value <= previous.value:
                raise forms.ValidationError(
                    'Новые показания должны быть больше предыдущих!'
                )
            
            # Проверяем, чтобы не было дубликатов за месяц
            existing = MeterReading.objects.filter(
                contract=contract,
                reading_date__year=reading_date.year,
                reading_date__month=reading_date.month
            ).exists()
            
            if existing:
                raise forms.ValidationError(
                    'Показания за этот месяц уже поданы!'
                )
        
        return cleaned_data


class BulkMeterReadingForm(forms.Form):
    """Форма для массовой подачи показаний"""
    readings = forms.JSONField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_readings(self):
        readings = self.cleaned_data['readings']
        if not readings:
            raise forms.ValidationError('Нет данных для обработки')
        
        # Валидация каждого показания
        for i, reading_data in enumerate(readings):
            if not all(k in reading_data for k in ['contract', 'date', 'value']):
                raise forms.ValidationError(f'Неполные данные в строке {i+1}')
            
            try:
                contract = Contract.objects.get(id=reading_data['contract'])
                # Проверка прав доступа
                if contract.consumer.user != self.user:
                    raise forms.ValidationError(f'Нет доступа к договору в строке {i+1}')
            except Contract.DoesNotExist:
                raise forms.ValidationError(f'Неверный договор в строке {i+1}')
        
        return readings