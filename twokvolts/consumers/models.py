from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Consumer(models.Model):
    USER_TYPE_CHOICES = [
        ('individual', 'Физическое лицо'),
        ('legal', 'Юридическое лицо'),
    ]
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='consumer')
    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    full_name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    personal_account = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.personal_account} - {self.full_name}"
