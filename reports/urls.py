from django.urls import path
from .views import *

app_name = 'reports'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('daily/', DailyReportView.as_view(), name='daily'),
    path('unit-numbers/', UnitNumberListView.as_view(), name='unit_numbers_list'),
    path('unit-numbers/create/', UnitNumberCreateView.as_view(), name='unit_numbers_create'),
    path('unit-numbers/<unit_number>/update/', UnitNumberUpdateView.as_view(), name='unit_numbers_update'),
    path('unit-numbers/<unit_number>/delete/', UnitNumberDeleteView.as_view(), name='unit_numbers_delete'),
]
