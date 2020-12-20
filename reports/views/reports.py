import datetime, math
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from reports.models import UsageData


TYPES = {
    '219': 'serial_number',
    '220': 'average_battery_voltage',
    '221': 'max_battery_voltage',
    '222': 'min_battery_voltage',
    '223': 'battery_critical_state_count',
    '224': '1_hour_samples_count',
    '225': 'lock_mode_entry_count',
    '226': 'factory_mode_entry_count',
    '227': 'gsm_sync_button_count',
    '228': 'stove_on_off_count',
    '229': 'daily_power_consumption',
    '230': 'left_stove_cooktime',
    '231': 'right_stove_cooktime',
    '232': 'others'
}


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/reports/reports.html'

    def get_context_data(self, **kwargs):
        done_unit_numbers = []
        report_data = []
        context = super().get_context_data(**kwargs)
        request = self.request

        if 'daterange' in request.GET:
            daterange = request.GET['daterange']
            daterange_splitted = daterange.split(' - ')
            from_date = daterange_splitted[0]
            from_date = datetime.datetime.strptime(from_date, '%m/%d/%Y')
            to_date = daterange_splitted[1]
            to_date = datetime.datetime.strptime(to_date, '%m/%d/%Y')

            data = UsageData.objects.filter(when_datetime__gte=from_date, when_datetime__lte=to_date).values(
                'unit_number',
                'data_type',
                'when_datetime__date'
            ).annotate(Sum('data_value'))

            # print(data)

            for item in data:
                if item['unit_number'] not in done_unit_numbers:
                    jitem_data = {
                        'unit_number': item['unit_number']
                    }
                    done_unit_numbers.append(item['unit_number'])

                    for jitem in data:
                        if item['unit_number'] ==  jitem['unit_number']:
                            jitem_data[TYPES[jitem['data_type']]] = jitem['data_value__sum']

                    jitem_data['serial_number'] = item['unit_number']
                    jitem_data['daily_cooking_time'] = jitem_data['left_stove_cooktime'] + jitem_data['right_stove_cooktime']
                    jitem_data['daily_cooking_time'] = math.ceil(jitem_data['daily_cooking_time'] * 100) / 100.0
                    jitem_data['average_power_consumption_per_use'] = jitem_data['daily_power_consumption'] / jitem_data['stove_on_off_count']
                    jitem_data['average_power_consumption_per_use'] = math.ceil(jitem_data['average_power_consumption_per_use'] * 100) / 100.0
                    jitem_data['average_cooking_time_per_use'] = jitem_data['daily_cooking_time'] / jitem_data['stove_on_off_count']
                    jitem_data['average_cooking_time_per_use'] = math.ceil(jitem_data['average_cooking_time_per_use'] * 100) / 100.0

                    report_data.append(jitem_data)            

            context['data'] = report_data

        return context
