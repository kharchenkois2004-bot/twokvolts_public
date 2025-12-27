# consumers/middleware.py
import time
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache


class UserActivityMiddleware(MiddlewareMixin):
    """Отслеживание активности пользователей"""

    def process_request(self, request):
        if request.user.is_authenticated:
            cache_key = f'user_activity_{request.user.id}'
            cache.set(cache_key, time.time(), 300)  # 5 минут
