from django.urls import path
from . import views

urlpatterns = [
    path('', views.showTasks, name='showTasks'),
    path('connect/', views.connect, name='connect'),
    path('job_return', views.job_return),
    path('diagram_data_return', views.diagram_data_return, name='diagram_data_return')
]