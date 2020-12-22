import datetime, math
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
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
        quick_statistics = {}
        prev_stove_on_off_count = 0
        context = super().get_context_data(**kwargs)
        request = self.request

        if 'daterange' in request.GET:
            daterange = request.GET['daterange']
            daterange_splitted = daterange.split(' - ')
            from_date = daterange_splitted[0]
            from_date = datetime.datetime.strptime(from_date, '%m/%d/%Y').date()
            from_date = str(from_date) + ' 00:00:00'
            to_date = daterange_splitted[1]
            to_date = datetime.datetime.strptime(to_date, '%m/%d/%Y').date()
            to_date = str(to_date) + ' 23:59:00'

            data = UsageData.objects.filter(
                when_datetime__gte=from_date,
                when_datetime__lte=to_date,
            ).values(
                'unit_number',
                'data_type',
                'when_datetime__date',
                'data_value'
            )

            for item in data:
                if (item['unit_number'], item['when_datetime__date']) not in done_unit_numbers:
                    jitem_data = {
                        'unit_number': item['unit_number'],
                        'when_datetime': item['when_datetime__date'],
                        TYPES[item['data_type']]: 0
                    }
                    done_unit_numbers.append(
                        (item['unit_number'], item['when_datetime__date'])
                    )

                    for jitem in data:
                        if not TYPES[jitem['data_type']] in jitem_data:
                            jitem_data[TYPES[jitem['data_type']]] = 0

                        if item['unit_number'] == jitem['unit_number'] and item['when_datetime__date'] == jitem['when_datetime__date']:
                            if jitem['data_type'] != '228' and jitem['data_type'] != '219':
                                jitem_data[TYPES[jitem['data_type']]] += float(jitem['data_value'])
                            else:
                                if jitem['data_type'] == '219':
                                    jitem_data[TYPES[jitem['data_type']]] = item['unit_number']
                                else:
                                    jitem_data[TYPES[jitem['data_type']]] = jitem['data_value']

                    report_data.append(jitem_data)            

            for item in report_data:
                prev_stove_on_off_count = item['stove_on_off_count']
                
                for jitem in report_data:
                    if item['serial_number'] == jitem['serial_number'] and item['when_datetime'] > jitem['when_datetime']:
                        item['stove_on_off_count'] = float(prev_stove_on_off_count) - float(jitem['stove_on_off_count'])
                        break

            for item in report_data:
                item['average_power_consumption_per_use'] = 0
                item['average_cooking_time_per_use'] = 0
                item['daily_cooking_time'] = item['left_stove_cooktime'] + item['right_stove_cooktime']
                item['daily_cooking_time'] = math.ceil(item['daily_cooking_time'] * 100) / 100.0
                
                if float(item['stove_on_off_count']) > 0:
                    item['average_power_consumption_per_use'] = item['daily_power_consumption'] / float(item['stove_on_off_count'])
                    item['average_cooking_time_per_use'] = item['daily_cooking_time'] / float(item['stove_on_off_count'])
                    item['average_power_consumption_per_use'] = math.ceil(item['average_power_consumption_per_use'] * 100) / 100.0
                    item['average_cooking_time_per_use'] = math.ceil(item['average_cooking_time_per_use'] * 100) / 100.0

            for item in report_data:
                daily_power_consumption = [float(jitem['daily_power_consumption']) for jitem in report_data]
                quick_statistics['average_power_consumption'] = sum(daily_power_consumption) / len(daily_power_consumption)
                quick_statistics['average_power_consumption'] = math.ceil(quick_statistics['average_power_consumption'] * 100) / 100

                left_stove_cooktime = [float(jitem['left_stove_cooktime']) for jitem in report_data]
                quick_statistics['average_left_stove_cooktime'] = sum(left_stove_cooktime) / len(left_stove_cooktime)
                quick_statistics['average_left_stove_cooktime'] = math.ceil(quick_statistics['average_left_stove_cooktime'] * 100) / 100

                right_stove_cooktime = [float(jitem['right_stove_cooktime']) for jitem in report_data]
                quick_statistics['average_right_stove_cooktime'] = sum(right_stove_cooktime) / len(right_stove_cooktime)
                quick_statistics['average_right_stove_cooktime'] = math.ceil(quick_statistics['average_right_stove_cooktime'] * 100) / 100

                daily_cooking_time = [float(jitem['daily_cooking_time']) for jitem in report_data]
                quick_statistics['average_cooking_time'] = sum(daily_cooking_time) / len(daily_cooking_time)
                quick_statistics['average_cooking_time'] = math.ceil(quick_statistics['average_cooking_time'] * 100) / 100

                stove_on_off_count = [float(jitem['stove_on_off_count']) for jitem in report_data]
                quick_statistics['average_stove_on_off_count'] = sum(stove_on_off_count) / len(stove_on_off_count)
                quick_statistics['average_stove_on_off_count'] = math.ceil(quick_statistics['average_stove_on_off_count'] * 100) / 100

                average_power_consumption_per_use = [float(jitem['average_power_consumption_per_use']) for jitem in report_data]
                quick_statistics['average_power_consumption_per_use'] = sum(average_power_consumption_per_use) / len(average_power_consumption_per_use)
                quick_statistics['average_power_consumption_per_use'] = math.ceil(quick_statistics['average_power_consumption_per_use'] * 100) / 100

                average_cooking_time_per_use = [float(jitem['average_cooking_time_per_use']) for jitem in report_data]
                quick_statistics['average_cooking_time_per_use'] = sum(average_cooking_time_per_use) / len(average_cooking_time_per_use)
                quick_statistics['average_cooking_time_per_use'] = math.ceil(quick_statistics['average_cooking_time_per_use'] * 100) / 100

            context['data'] = report_data
            context['quick_statistics'] = quick_statistics

        return context
