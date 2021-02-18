from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from reports.models import Country


class CountryListView(LoginRequiredMixin, ListView):
    template_name = 'reports/countries/list.html'
    model = Country
    context_object_name = 'countries'
    ordering = 'name'


class CountryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'reports/countries/create.html'
    model = Country
    fields = '__all__'
    success_url = reverse_lazy('reports:countries_list')
    success_message = "%(name)s was created successfully"


class CountryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'reports/countries/update.html'
    model = Country
    fields = '__all__'
    success_url = reverse_lazy('reports:countries_list')
    success_message = "%(name)s was updated successfully"


class CountryDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Country
    success_url = reverse_lazy('reports:countries_list')
    success_message = "%(name)s was deleted successfully"
