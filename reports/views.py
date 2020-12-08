import datetime
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from .forms import LoginForm
from angaza import Angaza


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


class LoginView(FormView):
    template_name = 'reports/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if not user.is_active:
                return render(self.request, self.template_name, context={
                    'error_message': 'User is not active',
                    'form': form
                })

            login(request=self.request, user=user)
            
            return redirect('reports:dashboard')

        return render(self.request, self.template_name, context={
            'error_message': 'Invalid credentials',
            'form': form
        })


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy('reports:login')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'


class DailyReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/daily.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        angaza = Angaza()
        angaza.set_auth(username='atec_iot', password='U*p9fJi31$$X')
        today = datetime.date.today()
        delta = datetime.timedelta(days=1)
        from_date = today - delta
        # data = angaza.get_usage_data(
        #     unit_number=74878232,
        #     from_when_dt='{}T00:00:00+00:00'.format(str(from_date)),
        #     to_when_dt='{}T00:00:00+00:00'.format(str(today))
        # )
        data = angaza.get_usage_data(
            unit_number=74878232,
            from_when_dt='2020-08-20T00:00:00+00:00',
            to_when_dt='2020-08-21T00:00:00+00:00'
        )
        temp_report_data = []
        report_data = {}

        for item in data['samples']:
            value = 0.0
            count = 0

            for jitem in data['samples']:
                if item['type'] == jitem['type']:
                    if jitem['type'] == 219:
                        value = jitem['value']
                    else:
                        value += jitem['value']
                    count += 1

            temp_data = list(
                filter(
                    lambda x: x['type'] == item['type'],
                    temp_report_data
                )
            )

            if len(temp_data) == 0:
                temp_report_data.append({
                    'type': item['type'],
                    'value': value,
                    'count': count
                })

                report_data[TYPES[str(item['type'])]] = value

        import math
        report_data['daily_cooking_time'] = report_data['left_stove_cooktime'] + report_data['right_stove_cooktime']
        report_data['daily_cooking_time'] = math.ceil(report_data['daily_cooking_time'] * 100) / 100.0
        report_data['average_power_consumption_per_use'] = report_data['daily_power_consumption'] / report_data['stove_on_off_count']
        report_data['average_power_consumption_per_use'] = math.ceil(report_data['average_power_consumption_per_use'] * 100) / 100.0
        report_data['average_cooking_time_per_use'] = report_data['daily_cooking_time'] / report_data['stove_on_off_count']
        report_data['average_cooking_time_per_use'] = math.ceil(report_data['average_cooking_time_per_use'] * 100) / 100.0

        context['data'] = [report_data]

        return context
