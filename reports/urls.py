from django.urls import path
from .views import *

app_name = 'reports'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', ReportsView.as_view(), name='reports'),
    path('exports/', ExportView.as_view(), name='exports'),
    path('countries/', CountryListView.as_view(), name='countries_list'),
    path('countries/create/', CountryCreateView.as_view(), name='countries_create'),
    path('countries/<pk>/update/', CountryUpdateView.as_view(), name='countries_update'),
    path('countries/<pk>/delete/', CountryDeleteView.as_view(), name='countries_delete'),
    path('unit-numbers/', UnitNumberListView.as_view(), name='unit_numbers_list'),
    path('unit-numbers/create/', UnitNumberCreateView.as_view(), name='unit_numbers_create'),
    path('unit-numbers/<unit_number>/update/', UnitNumberUpdateView.as_view(), name='unit_numbers_update'),
    path('unit-numbers/<unit_number>/delete/', UnitNumberDeleteView.as_view(), name='unit_numbers_delete'),
]
