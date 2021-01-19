from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from reports.models import UnitNumber


class UnitNumberListView(LoginRequiredMixin, ListView):
    template_name = 'reports/unit_numbers/list.html'
    model = UnitNumber
    context_object_name = 'unit_numbers'
    ordering = 'unit_number'


class UnitNumberCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'reports/unit_numbers/create.html'
    model = UnitNumber
    fields = '__all__'
    success_url = reverse_lazy('reports:unit_numbers_list')
    
    def get_success_message(self, cleaned_data: Dict[str, str]) -> str:
        return str(cleaned_data['unit_number']) + ' was created successfully'


class UnitNumberUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'reports/unit_numbers/update.html'
    model = UnitNumber
    fields = '__all__'
    success_url = reverse_lazy('reports:unit_numbers_list')

    def get_object(self) -> QuerySet:
        return get_object_or_404(UnitNumber, unit_number=self.kwargs['unit_number'])

    def get_success_message(self, cleaned_data: Dict[str, str]) -> str:
        return str(cleaned_data['unit_number']) + ' was updated successfully'


class UnitNumberDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = UnitNumber
    success_url = reverse_lazy('reports:unit_numbers_list')

    def get_object(self) -> QuerySet:
        return get_object_or_404(UnitNumber, unit_number=self.kwargs['unit_number'])

    def get_success_message(self, cleaned_data: Dict[str, str]) -> str:
        return str(cleaned_data['unit_number']) + ' was deleted successfully'
