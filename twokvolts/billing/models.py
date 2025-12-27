from django.db import models
from contracts.models import Contract
from meter_readings.models import MeterReading


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Выставлен'),
        ('paid', 'Оплачен'),
        ('overdue', 'Просрочен'),
    ]
    contract = models.ForeignKey(Contract,
                                 on_delete=models.CASCADE,
                                 related_name='invoices')
    period = models.DateField()  # Период начисления
    meter_reading = models.OneToOneField(MeterReading,
                                         on_delete=models.PROTECT,
                                         null=True) # Связь с показанием
    consumption = models.DecimalField(max_digits=12,
                                      decimal_places=4)  # Расход
    amount = models.DecimalField(max_digits=12,
                                 decimal_places=2)  # Сумма к оплате
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES, default='issued')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()  # Дата, до которой нужно оплатить

    def __str__(self):
        return f"Счет #{self.id} за {self.period.strftime('%Y-%m')}"
