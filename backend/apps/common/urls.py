from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.GetHealth.as_view()),
]
