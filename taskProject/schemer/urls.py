from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_tasks, name='show_tasks'),
    path('api/connect', views.connect, name='connect'),
    path('api/job_return', views.job_return, name='job_return'),
    path('api/diagram_new_task', views.diagram_new_task, name='diagram_new_task'),
    path('api/diagram_remove_task', views.diagram_remove_task, name='diagram_remove_task'),
    path('api/diagram_new_dependency', views.diagram_new_dependency, name='diagram_new_dependency'),
    path('api/diagram_edit_dependency', views.diagram_edit_dependency, name='diagram_edit_dependency'),
    path('api/diagram_remove_dependencies',views.diagram_remove_dependencies, name='diagram_remove_dependencies')
]