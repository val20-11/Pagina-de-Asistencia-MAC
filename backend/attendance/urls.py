from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_attendance, name='register_attendance'),
    path('stats/', views.get_student_stats, name='student_stats'),
    path('recent/', views.get_recent_attendances, name='recent_attendances'),
    path('my/', views.get_my_attendances, name='my_attendances'),
    path('external/my/', views.get_external_user_attendances, name='external_user_attendances'),
    path('external/stats/', views.get_external_user_stats, name='external_user_stats'),
]