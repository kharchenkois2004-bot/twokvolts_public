from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from consumers.models import Consumer
from contracts.models import Contract
from meter_readings.models import MeterReading
from billing.models import Invoice
from payments.models import Payment


class AccountsHomeView(LoginRequiredMixin, TemplateView):
    """Главная страница личного кабинета"""
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            consumer = Consumer.objects.get(user=user)
            context['consumer'] = consumer
            
            # Получаем активные договоры
            active_contracts = Contract.objects.filter(
                consumer=consumer, 
                is_active=True
            ).select_related('tariff')
            context['active_contracts'] = active_contracts
            
            # Последние показания
            latest_readings = MeterReading.objects.filter(
                contract__in=active_contracts
            ).order_by('-reading_date')[:5]
            context['latest_readings'] = latest_readings
            
            # Текущие счета
            current_invoices = Invoice.objects.filter(
                contract__in=active_contracts,
                status='issued'
            ).order_by('due_date')[:3]
            context['current_invoices'] = current_invoices
            
            # Последние платежи
            recent_payments = Payment.objects.filter(
                invoice__contract__in=active_contracts
            ).order_by('-payment_date')[:5]
            context['recent_payments'] = recent_payments
            
            # Статистика
            total_debt = Invoice.objects.filter(
                contract__in=active_contracts,
                status='issued'
            ).aggregate(total=Sum('amount'))['total'] or 0
            context['total_debt'] = total_debt
            
            # Уведомления
            overdue_invoices = Invoice.objects.filter(
                contract__in=active_contracts,
                status='issued',
                due_date__lt=timezone.now().date()
            ).count()
            context['overdue_invoices'] = overdue_invoices
            
        except Consumer.DoesNotExist:
            context['consumer'] = None
        
        return context


class DashboardOverview(LoginRequiredMixin, TemplateView):
    """Обзорная панель с графиками и статистикой"""
    template_name = 'dashboard/overview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consumer = get_object_or_404(Consumer, user=self.request.user)
        
        # Статистика потребления за последние 6 месяцев
        six_months_ago = timezone.now().date() - timedelta(days=180)
        
        invoices = Invoice.objects.filter(
            contract__consumer=consumer,
            period__gte=six_months_ago
        ).order_by('period')
        
        consumption_data = []
        amount_data = []
        labels = []
        
        for invoice in invoices:
            consumption_data.append(float(invoice.consumption))
            amount_data.append(float(invoice.amount))
            labels.append(invoice.period.strftime('%b %Y'))
        
        context['consumption_data'] = consumption_data
        context['amount_data'] = amount_data
        context['labels'] = labels
        
        return context


class ConsumptionStatsView(LoginRequiredMixin, TemplateView):
    """Детальная статистика потребления"""
    template_name = 'dashboard/stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consumer = get_object_or_404(Consumer, user=self.request.user)
        
        year = self.request.GET.get('year', timezone.now().year)
        
        # Статистика по месяцам за выбранный год
        monthly_stats = []
        for month in range(1, 13):
            invoices = Invoice.objects.filter(
                contract__consumer=consumer,
                period__year=year,
                period__month=month
            )
            
            if invoices.exists():
                total_consumption = invoices.aggregate(Sum('consumption'))['consumption__sum'] or 0
                total_amount = invoices.aggregate(Sum('amount'))['amount__sum'] or 0
                monthly_stats.append({
                    'month': month,
                    'consumption': total_consumption,
                    'amount': total_amount,
                    'invoices_count': invoices.count()
                })
        
        context['monthly_stats'] = monthly_stats
        context['selected_year'] = year
        context['available_years'] = range(2020, timezone.now().year + 1)
        
        return context


class NotificationsView(LoginRequiredMixin, ListView):
    """Страница уведомлений"""
    template_name = 'dashboard/notifications.html'
    context_object_name = 'notifications'
    
    def get_queryset(self):
        consumer = get_object_or_404(Consumer, user=self.request.user)
        
        notifications = []
        
        # Просроченные счета
        overdue = Invoice.objects.filter(
            contract__consumer=consumer,
            status='issued',
            due_date__lt=timezone.now().date()
        )
        for invoice in overdue:
            notifications.append({
                'type': 'warning',
                'title': 'Просроченный счет',
                'message': f'Счет #{invoice.id} за {invoice.period.strftime("%B %Y")} просрочен',
                'date': invoice.due_date,
                'link': invoice.get_absolute_url()
            })
        
        # Предстоящие сроки оплаты (в течение 3 дней)
        upcoming = Invoice.objects.filter(
            contract__consumer=consumer,
            status='issued',
            due_date__range=[
                timezone.now().date(),
                timezone.now().date() + timedelta(days=3)
            ]
        )
        for invoice in upcoming:
            notifications.append({
                'type': 'info',
                'title': 'Скоро срок оплаты',
                'message': f'Счет #{invoice.id} нужно оплатить до {invoice.due_date}',
                'date': invoice.due_date,
                'link': invoice.get_absolute_url()
            })
        
        # Новые счета (последние 7 дней)
        new_invoices = Invoice.objects.filter(
            contract__consumer=consumer,
            issue_date__gte=timezone.now().date() - timedelta(days=7)
        )
        for invoice in new_invoices:
            notifications.append({
                'type': 'success',
                'title': 'Новый счет',
                'message': f'Выставлен счет #{invoice.id} за {invoice.period.strftime("%B %Y")}',
                'date': invoice.issue_date,
                'link': invoice.get_absolute_url()
            })
        
        return sorted(notifications, key=lambda x: x['date'], reverse=True)


# Быстрые действия
class QuickMeterReading(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/quick_reading.html'


class QuickPaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/quick_pay.html'


# Обработчики ошибок
def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)