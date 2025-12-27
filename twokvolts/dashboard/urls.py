from django.urls import path
from . import views

urlpatterns = [
    # Основные страницы личного кабинета
    path('', views.AccountsHomeView.as_view(), name='dashboard'),
    path('overview/', views.DashboardOverview.as_view(), name='dashboard_overview'),
    path('stats/', views.ConsumptionStatsView.as_view(), name='consumption_stats'),
    path('notifications/', views.NotificationsView.as_view(), name='notifications'),
    
    # Быстрые действия
    path('quick-reading/', views.QuickMeterReading.as_view(), name='quick_reading'),
    path('quick-pay/', views.QuickPaymentView.as_view(), name='quick_pay'),
]