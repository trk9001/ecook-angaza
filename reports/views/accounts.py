from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from reports.forms import LoginForm
from django.contrib.auth import authenticate, login


class LoginView(FormView):
    template_name = 'reports/accounts/login.html'
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
            
            return redirect('reports:reports')

        return render(self.request, self.template_name, context={
            'error_message': 'Invalid credentials',
            'form': form
        })


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy('reports:login')
