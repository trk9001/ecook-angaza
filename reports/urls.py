from django.urls import path
from .views import LoginView, LogoutView, DashboardView, DailyReportView

app_name = 'reports'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('daily/', DailyReportView.as_view(), name='daily'),
]
