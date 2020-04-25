from django.urls import path

from cdzstat import views

app_name = 'cdzstat'
urlpatterns = [
    path('cdzstat/collect_statistic', views.collector, name='col_stat')
]
