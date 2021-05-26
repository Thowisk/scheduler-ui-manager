from django.urls import path
from . import views

urlpatterns = [
    path('', views.showTasks, name='showTasks'),
    path('connect/', views.connect, name='connect'),
    path('job_return', views.job_return)
]