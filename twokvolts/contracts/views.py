from django.shortcuts import render
from django.views.generic import ListView
from .models import Tariff


class TariffsListView(ListView):
    template_name = 'pages/tariffs.html'
    model = Tariff
    context_object_name = "all_tariffs"
