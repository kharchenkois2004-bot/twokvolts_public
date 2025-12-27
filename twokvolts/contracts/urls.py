from django.urls import path
from . import views


urlpatterns = [
    # path('', , name='list'),
    path('', views.TariffsListView.as_view(), name='tariffs'),
]