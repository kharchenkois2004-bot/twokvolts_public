# dashboard/context_processors.py
from django.core.cache import cache

def dashboard_context(request):
    """Добавляет контекст для всех шаблонов dashboard"""
    context = {}
    
    if request.user.is_authenticated:
        # Проверяем активность пользователя
        cache_key = f'user_activity_{request.user.id}'
        last_activity = cache.get(cache_key)
        
        context['last_activity'] = last_activity
        context['is_user_active'] = last_activity is not None
    
    return context