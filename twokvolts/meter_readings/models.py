from django.db import models
from contracts.models import Contract


class MeterReading(models.Model):
    contract = models.ForeignKey(Contract,
                                 on_delete=models.CASCADE,
                                 related_name='readings')
    reading_date = models.DateField()
    value = models.DecimalField(max_digits=12,
                                decimal_places=4)  # Значение счетчика в кВт*ч
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-reading_date']
        unique_together = ['contract', 'reading_date']