import csv
import codecs
from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from reports.models import Country, UnitNumber
from reports.forms import ImportForm


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


class MapView(TemplateView):
    template_name = 'reports/map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unit_numbers'] = UnitNumber.objects.all()

        return context


class ImportView(TemplateView):
    template_name = 'reports/unit_numbers/import.html'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['form'] = ImportForm()

        return context

    def post(self, request, *args, **kwargs):
        form = ImportForm(files=request.FILES)

        if not form.is_valid():
            return render(request, self.template_name, {
                'form': form
            })

        file = form.cleaned_data['csv']
        reader = csv.DictReader(codecs.iterdecode(file, 'utf-8'))
        counter = 0

        for row in reader:
            country, created = Country.objects.get_or_create(
                name=row['Country'],
                defaults={
                    'cost': 0.00
                }
            )
            country = country.__dict__

            UnitNumber.objects.update_or_create(
                unit_number=row['Unit Number'],
                defaults={
                    'name': row['Name'],
                    'country_id': country['id'],
                    'description': row['Description'],
                    'latitude': row['Latitude'] if row['Latitude'] != '' else 0.00,
                    'longitude': row['Longitude'] if row['Longitude'] != '' else 0.00,
                }
            )

            counter += 1

        messages.success(request, f'Total {counter} row(s) has been inserted')

        return redirect('reports:unit_numbers_list')
