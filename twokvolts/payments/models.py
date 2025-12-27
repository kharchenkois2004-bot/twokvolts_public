from django.db import models
from billing.models import Invoice


class Payment(models.Model):
    METHOD_CHOICES = [
        ('Cash', 'Наличный'),
        ('Online', 'Безналичный'),
        ('Bank transfer', 'Банковский перевод'),
    ]
    invoice = models.ForeignKey(Invoice,
                                on_delete=models.PROTECT,
                                related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    external_id = models.CharField(max_length=100, blank=True)
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Логика обновления статуса счета после оплаты
        total_paid = self.invoice.payments.aggregate(total=models.Sum('amount'))['total'] or 0
        if total_paid >= self.invoice.amount:
            self.invoice.status = 'paid'
            self.invoice.save()
