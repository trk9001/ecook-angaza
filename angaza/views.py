from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from .forms import LoginForm


class LoginView(FormView):
    template_name = 'angaza/login.html'
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
            
            return redirect('angaza:dashboard')

        return render(self.request, self.template_name, context={
            'error_message': 'Invalid credentials',
            'form': form
        })


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy('angaza:login')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'angaza/dashboard.html'
