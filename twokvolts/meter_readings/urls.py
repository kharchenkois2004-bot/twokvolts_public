from django.urls import path
from . import views

app_name = 'meter_readings'

urlpatterns = [
    path('', views.MeterReadingListView.as_view(), name='list'),
    path('submit/', views.MeterReadingCreateView.as_view(), name='submit'),
    path('history/', views.MeterReadingHistoryView.as_view(), name='history'),
    path('<int:pk>/', views.MeterReadingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.MeterReadingUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.MeterReadingDeleteView.as_view(), name='delete'),
    path('bulk-submit/', views.BulkMeterReadingView.as_view(), name='bulk_submit'),
]