from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('register/', views.register_project, name='register_project'),
    path('monitor/', views.monitor_projects, name='monitor_projects'),
    path('webhook/git/', views.webhook_git, name='webhook_git'),
    path('delete/<int:pk>/', views.delete_project, name='delete_project'),
    path('mark-viewed/<int:pk>/', views.mark_push_viewed, name='mark_push_viewed'),
]