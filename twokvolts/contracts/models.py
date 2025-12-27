from django.db import models
from consumers.models import Consumer


class Tariff(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    rate = models.DecimalField(max_digits=10,
                               decimal_places=4)  # Цена за кВт*ч (руб.)
    is_active = models.BooleanField(default=True)


class Contract(models.Model):
    consumer = models.ForeignKey(Consumer, 
                                 on_delete=models.CASCADE,
                                 related_name='contracts')
    tariff = models.ForeignKey(Tariff,
                               on_delete=models.PROTECT)
    contract_number = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    meter_number = models.CharField(max_length=50)
    meter_installation_date = models.DateField()
