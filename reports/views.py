import datetime
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from .forms import LoginForm
from angaza import Angaza


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
        # context['data'] = angaza.get_usage_data(
        #     unit_number=74878232,
        #     from_when_dt='{}T00:00:00+00:00'.format(str(from_date)),
        #     to_when_dt='{}T00:00:00+00:00'.format(str(today))
        # )
        context['data'] = angaza.get_usage_data(
            unit_number=74878232,
            from_when_dt='2020-08-20T00:00:00+00:00',
            to_when_dt='2020-08-21T00:00:00+00:00'
        )

        return context
