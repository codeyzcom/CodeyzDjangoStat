from django.urls import path

from cdzstat import views

app_name = 'cdzstat'
urlpatterns = [
    path('cdzstat/collect_statistic', views.dummy_view, name='dummy'),
    path('cdzstat/dashboard/', views.dashboard, name='dashboard'),
    path('cdzstat/exceptions/', views.exceptions, name='exceptions'),
    path('cdzstat/sessions/', views.sessions_board, name='sessions'),
]
