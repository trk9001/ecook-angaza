import datetime, math, os, csv
from urllib.parse import urlencode
from django.http.response import Http404, HttpResponse
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from reports.models import Country, DailyUsageData, UnitNumber
from reports.exports import Exporter, Csv, Pdf


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/reports/reports.html'

    def get_context_data(self, **kwargs):
        quick_statistics = {}
        query_params = {}
        total_cost_list = []
        context = super().get_context_data(**kwargs)
        request = self.request
        unit_numbers = UnitNumber.objects.all().order_by('unit_number')

        if 'daterange' in request.GET:
            total = {}
            daterange = request.GET['daterange']
            query_params['daterange'] = daterange
            daterange_splitted = daterange.split(' - ')
            from_date = daterange_splitted[0]
            from_date = datetime.datetime.strptime(from_date, '%m/%d/%Y').date()
            from_date = str(from_date)
            to_date = daterange_splitted[1]
            to_date = datetime.datetime.strptime(to_date, '%m/%d/%Y').date()
            to_date = str(to_date)
            usage_data_filter = {
                'when_date__gte': from_date,
                'when_date__lte': to_date
            }

            if 'country' in request.GET and request.GET['country'] != 'all':
                query_params['country'] = request.GET['country']
                country = Country.objects.filter(name=request.GET['country'])

                if country.exists():
                    unit_numbers = country.first().unitnumber_set.all().order_by('unit_number')
                    usage_data_filter['serial_number__in'] = list(
                        map(lambda x: x.unit_number, unit_numbers)
                    )
                    query_params['unit_number'] = 'All'

            if 'unit_number' in request.GET and request.GET['unit_number'] != 'all':
                usage_data_filter['serial_number'] = request.GET['unit_number']
                query_params['unit_number'] = request.GET['unit_number']

            data = DailyUsageData.objects.filter(**usage_data_filter).order_by('-when_date')

            if data.count() > 0:
                for item in data:
                    obj = UnitNumber.objects.get(unit_number=item.serial_number)

                    try:
                        cost = math.ceil((item.daily_power_consumption * obj.country.cost) * 100) / 100
                        item.cost = cost

                        if cost > 0:
                            total_cost_list.append(cost)
                    except:
                        item.cost = 0.00

                total_cost = math.ceil(sum(total_cost_list) * 100) / 100
                quick_statistics['average_cost'] = total_cost / data.count()
                quick_statistics['average_cost'] = math.ceil(quick_statistics['average_cost'] * 100) / 100
                quick_statistics['average_cost_exclude_zero'] = total_cost / len(total_cost_list) \
                    if len(total_cost_list) > 0 else 0.00
                quick_statistics['average_cost_exclude_zero'] = math.ceil(
                    quick_statistics['average_cost_exclude_zero'] * 100
                ) / 100

                daily_power_consumption_list = [item.daily_power_consumption for item in data]
                daily_power_consumption_list_exclude_zero_list = [item.daily_power_consumption for item in data if item.daily_power_consumption > 0]
                quick_statistics['average_power_consumption'] = sum(daily_power_consumption_list) / len(daily_power_consumption_list)
                quick_statistics['average_power_consumption'] = math.ceil(quick_statistics['average_power_consumption'] * 100) / 100
                quick_statistics['average_power_consumption_exclude_zero'] = sum(daily_power_consumption_list_exclude_zero_list) / len(daily_power_consumption_list_exclude_zero_list) \
                    if len(daily_power_consumption_list_exclude_zero_list) > 0 else 0
                quick_statistics['average_power_consumption_exclude_zero'] = math.ceil(quick_statistics['average_power_consumption_exclude_zero'] * 100) / 100

                left_stove_cooktime = [item.left_stove_cooktime for item in data]
                left_stove_cooktime_exclude_zero_list = [item.left_stove_cooktime for item in data if item.left_stove_cooktime > 0]
                quick_statistics['average_left_stove_cooktime'] = sum(left_stove_cooktime) / len(left_stove_cooktime)
                quick_statistics['average_left_stove_cooktime'] = math.ceil(quick_statistics['average_left_stove_cooktime'] * 100) / 100
                quick_statistics['average_left_stove_cooktime_exclude_zero'] = sum(left_stove_cooktime_exclude_zero_list) / len(left_stove_cooktime_exclude_zero_list) \
                    if len(left_stove_cooktime_exclude_zero_list) > 0 else 0
                quick_statistics['average_left_stove_cooktime_exclude_zero'] = math.ceil(quick_statistics['average_left_stove_cooktime_exclude_zero'] * 100) / 100

                right_stove_cooktime = [item.right_stove_cooktime for item in data]
                right_stove_cooktime_exclude_zero_list = [item.right_stove_cooktime for item in data if item.right_stove_cooktime > 0]
                quick_statistics['average_right_stove_cooktime'] = sum(right_stove_cooktime) / len(right_stove_cooktime)
                quick_statistics['average_right_stove_cooktime'] = math.ceil(quick_statistics['average_right_stove_cooktime'] * 100) / 100
                quick_statistics['average_right_stove_cooktime_exclude_zero'] = sum(right_stove_cooktime_exclude_zero_list) / len(right_stove_cooktime_exclude_zero_list) \
                    if len(right_stove_cooktime_exclude_zero_list) > 0 else 0
                quick_statistics['average_right_stove_cooktime_exclude_zero'] = math.ceil(quick_statistics['average_right_stove_cooktime_exclude_zero'] * 100) / 100

                daily_cooking_time = [item.daily_cooking_time for item in data]
                daily_cooking_time_exclude_zero_list = [item.daily_cooking_time for item in data if item.daily_cooking_time > 0]
                quick_statistics['average_cooking_time'] = sum(daily_cooking_time) / len(daily_cooking_time)
                quick_statistics['average_cooking_time'] = math.ceil(quick_statistics['average_cooking_time'] * 100) / 100
                quick_statistics['average_cooking_time_exclude_zero'] = sum(daily_cooking_time_exclude_zero_list) / len(daily_cooking_time_exclude_zero_list) \
                    if len(daily_cooking_time_exclude_zero_list) > 0 else 0
                quick_statistics['average_cooking_time_exclude_zero'] = math.ceil(quick_statistics['average_cooking_time_exclude_zero'] * 100) / 100
                quick_statistics['percentage_of_days_used'] = (len(daily_cooking_time_exclude_zero_list) / len(daily_cooking_time)) * 100
                quick_statistics['percentage_of_days_used'] = math.ceil(quick_statistics['percentage_of_days_used'] * 100) / 100

                stove_on_off_count = [item.stove_on_off_count for item in data]
                stove_on_off_count_exclude_zero_list = [item.stove_on_off_count for item in data if item.stove_on_off_count > 0]
                quick_statistics['average_stove_on_off_count'] = sum(stove_on_off_count) / len(stove_on_off_count)
                quick_statistics['average_stove_on_off_count'] = math.ceil(quick_statistics['average_stove_on_off_count'] * 100) / 100
                quick_statistics['average_stove_on_off_count_exclude_zero'] = sum(stove_on_off_count_exclude_zero_list) / len(stove_on_off_count_exclude_zero_list) \
                    if len(stove_on_off_count_exclude_zero_list) > 0 else 0
                quick_statistics['average_stove_on_off_count_exclude_zero'] = math.ceil(quick_statistics['average_stove_on_off_count_exclude_zero'] * 100) / 100

                quick_statistics['average_power_consumption_per_use'] = math.ceil((quick_statistics['average_power_consumption'] / quick_statistics['average_stove_on_off_count']) * 100) / 100
                quick_statistics['average_power_consumption_per_use_exclude_zero'] = math.ceil((quick_statistics['average_power_consumption_exclude_zero'] / quick_statistics['average_stove_on_off_count_exclude_zero']) * 100) / 100

                quick_statistics['average_cooking_time_per_use'] = math.ceil((quick_statistics['average_cooking_time'] / quick_statistics['average_stove_on_off_count']) * 100) / 100
                quick_statistics['average_cooking_time_per_use_exclude_zero'] = math.ceil((quick_statistics['average_cooking_time_exclude_zero'] / quick_statistics['average_stove_on_off_count_exclude_zero']) * 100) / 100

                total['daily_power_consumption'] = sum(
                    [item.daily_power_consumption for item in data]
                )
                total['left_stove_cooktime'] = sum(
                    [item.left_stove_cooktime for item in data]
                )
                total['right_stove_cooktime'] = sum(
                    [item.right_stove_cooktime for item in data]
                )
                total['daily_cooking_time'] = sum(
                    [item.daily_cooking_time for item in data]
                )
                total['total_cost'] = total_cost

                context['data'] = data
                context['quick_statistics'] = quick_statistics
                context['total'] = total
            
        context['unit_numbers'] = unit_numbers
        context['countries'] = Country.objects.all().order_by('name')
        context['query_params'] = query_params
        context['query_params_encoded'] = urlencode(query_params)

        return context


class ExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if 'daterange' in request.GET:
            daterange = request.GET['daterange']
            daterange_splitted = daterange.split(' - ')
            from_date = daterange_splitted[0]
            from_date = datetime.datetime.strptime(from_date, '%m/%d/%Y').date()
            from_date = str(from_date)
            to_date = daterange_splitted[1]
            to_date = datetime.datetime.strptime(to_date, '%m/%d/%Y').date()
            to_date = str(to_date)
            usage_data_filter = {
                'when_date__gte': from_date,
                'when_date__lte': to_date
            }

            if 'country' in request.GET and request.GET['country'] != 'all':
                country = Country.objects.filter(name=request.GET['country'])

                if country.exists():
                    unit_numbers = country.first().unitnumber_set.all().order_by('unit_number')
                    usage_data_filter['serial_number__in'] = list(
                        map(lambda x: x.unit_number, unit_numbers)
                    )

            if 'unit_number' in request.GET and request.GET['unit_number'] != 'all':
                usage_data_filter['serial_number'] = request.GET['unit_number']

            data = DailyUsageData.objects.filter(**usage_data_filter).order_by('-when_date')

            if data.count() > 0:
                if request.GET['format'] == 'csv':
                    return Exporter(Csv).export(data=data)
                elif request.GET['format'] == 'pdf':
                    return Exporter(Pdf).export(data=data)

        return Http404
