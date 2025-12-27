from django.shortcuts import render

# meter_readings/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import MeterReading
from contracts.models import Contract
from consumers.models import Consumer
from .forms import MeterReadingForm, BulkMeterReadingForm

class MeterReadingListView(LoginRequiredMixin, ListView):
    """Список показаний счетчиков"""
    model = MeterReading
    template_name = 'meter_readings/list.html'
    context_object_name = 'readings'
    paginate_by = 10
    
    def get_queryset(self):
        consumer = get_object_or_404(Consumer, user=self.request.user)
        contracts = Contract.objects.filter(consumer=consumer, is_active=True)
        
        queryset = MeterReading.objects.filter(
            contract__in=contracts
        ).select_related('contract', 'contract__tariff')
        
        # Фильтрация по договору
        contract_id = self.request.GET.get('contract')
        if contract_id:
            queryset = queryset.filter(contract_id=contract_id)
        
        # Фильтрация по дате
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(reading_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(reading_date__lte=date_to)
        
        return queryset.order_by('-reading_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consumer = get_object_or_404(Consumer, user=self.request.user)
        context['contracts'] = Contract.objects.filter(
            consumer=consumer, 
            is_active=True
        )
        return context


class MeterReadingCreateView(LoginRequiredMixin, CreateView):
    """Подача новых показаний"""
    model = MeterReading
    form_class = MeterReadingForm
    template_name = 'meter_readings/submit.html'
    success_url = reverse_lazy('meter_readings:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.submitted_by = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request, 
            'Показания успешно отправлены!'
        )
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Пожалуйста, исправьте ошибки в форме.'
        )
        return super().form_invalid(form)


class MeterReadingUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование показаний"""
    model = MeterReading
    form_class = MeterReadingForm
    template_name = 'meter_readings/edit.html'
    
    def get_queryset(self):
        consumer = get_object_or_404(Consumer, user=self.request.user)
        contracts = Contract.objects.filter(consumer=consumer)
        return MeterReading.objects.filter(contract__in=contracts)
    
    def get_success_url(self):
        return reverse_lazy('meter_readings:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(
            self.request,
            'Показания успешно обновлены!'
        )
        return super().form_valid(form)


class MeterReadingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление показаний"""
    model = MeterReading
    template_name = 'meter_readings/confirm_delete.html'
    success_url = reverse_lazy('meter_readings:list')
    
    def get_queryset(self):
        consumer = get_object_or_404(Consumer, user=self.request.user)
        contracts = Contract.objects.filter(consumer=consumer)
        return MeterReading.objects.filter(contract__in=contracts)
    
    def delete(self, request, *args, **kwargs):
        messages.success(
            request,
            'Показания успешно удалены!'
        )
        return super().delete(request, *args, **kwargs)


class MeterReadingDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр показаний"""
    model = MeterReading
    template_name = 'meter_readings/detail.html'
    context_object_name = 'reading'
    
    def get_queryset(self):
        consumer = get_object_or_404(Consumer, user=self.request.user)
        contracts = Contract.objects.filter(consumer=consumer)
        return MeterReading.objects.filter(contract__in=contracts)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем предыдущие показания для сравнения
        previous = MeterReading.objects.filter(
            contract=self.object.contract,
            reading_date__lt=self.object.reading_date
        ).order_by('-reading_date').first()
        
        if previous:
            consumption = self.object.value - previous.value
            context['previous_reading'] = previous
            context['consumption'] = consumption
        
        return context


class MeterReadingHistoryView(LoginRequiredMixin, TemplateView):
    """История показаний с графиком"""
    template_name = 'meter_readings/history.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consumer = get_object_or_404(Consumer, user=self.request.user)
        contract_id = self.request.GET.get('contract')
        
        if contract_id:
            contract = get_object_or_404(Contract, id=contract_id, consumer=consumer)
            readings = MeterReading.objects.filter(
                contract=contract
            ).order_by('reading_date')
            
            # Подготовка данных для графика
            dates = [r.reading_date.strftime('%Y-%m') for r in readings]
            values = [float(r.value) for r in readings]
            
            context['readings'] = readings
            context['contract'] = contract
            context['chart_data'] = {
                'dates': dates,
                'values': values
            }
        
        context['contracts'] = Contract.objects.filter(
            consumer=consumer, 
            is_active=True
        )
        
        return context


class BulkMeterReadingView(LoginRequiredMixin, CreateView):
    """Массовая подача показаний (для нескольких договоров сразу)"""
    template_name = 'meter_readings/bulk_submit.html'
    form_class = BulkMeterReadingForm
    success_url = reverse_lazy('meter_readings:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Обработка массовой подачи
        readings_data = form.cleaned_data['readings']
        created_count = 0
        
        for data in readings_data:
            MeterReading.objects.create(
                contract=data['contract'],
                reading_date=data['date'],
                value=data['value'],
                submitted_by=self.request.user
            )
            created_count += 1
        
        messages.success(
            self.request,
            f'Успешно подано {created_count} показаний!'
        )
        return super().form_valid(form)
