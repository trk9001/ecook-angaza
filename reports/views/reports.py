import datetime, math, os, csv
from urllib.parse import urlencode
from django.http.response import Http404, HttpResponse
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from reports.models import Country, DailyUsageData, UnitNumber


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/reports/reports.html'

    def get_context_data(self, **kwargs):
        quick_statistics = {}
        query_params = {}
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

            if 'unit_number' in request.GET and request.GET['unit_number'] != 'all':
                usage_data_filter['serial_number'] = request.GET['unit_number']
                query_params['unit_number'] = request.GET['unit_number']

            data = DailyUsageData.objects.filter(**usage_data_filter).order_by('-when_date')

            if data.count() > 0:
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

            if 'unit_number' in request.GET and request.GET['unit_number'] != 'all':
                usage_data_filter['serial_number'] = request.GET['unit_number']

            data = DailyUsageData.objects.filter(**usage_data_filter).order_by('-when_date')

            if data.count() > 0:
                file = None

                if request.GET['format'] == 'csv':
                    file = self.export_to_csv(data)
                elif request.GET['format'] == 'pdf':
                    file = self.export_to_pdf(data)

                if file is not None:
                    with open(file, 'r') as f:
                        response = HttpResponse(f.read(), content_type='application/vnd.ms-excel')
                        response['Content-Disposition'] = f'inline; filename={os.path.basename(file)}'

                        return response

        return Http404

    def export_to_csv(self, data):
        file_name = 'data.csv'
        file_to_write = f'assets/files/{file_name}'

        if os.path.exists(file_to_write):
            os.remove(file_to_write)

        with open(file_to_write, 'w') as file:
            fieldnames = [
                'Serial Number',
                'Date',
                'Daily Power Consumption (KWh)',
                'Left Stove Cooking Time',
                'Right Stove Cooking Time',
                'Daily Cooking Time',
                'Stove On/Off Count',
                'Average Power Consumption per use',
                'Average Cooking time per use'
            ]
            write = csv.DictWriter(file, fieldnames=fieldnames)

            write.writeheader()

            for item in data:
                write.writerow(
                    {
                        'Serial Number': item.serial_number,
                        'Date': item.when_date,
                        'Daily Power Consumption (KWh)': item.daily_power_consumption,
                        'Left Stove Cooking Time': item.left_stove_cooktime,
                        'Right Stove Cooking Time': item.right_stove_cooktime ,
                        'Daily Cooking Time': item.daily_cooking_time,
                        'Stove On/Off Count': item.stove_on_off_count,
                        'Average Power Consumption per use': item.average_power_consumption_per_use,
                        'Average Cooking time per use': item.average_cooking_time_per_use
                    }
                )

        return file_to_write

    def export_to_pdf(self, data):
        pass
