from django.urls import path
from . import views

urlpatterns = [
    path('banco-central/', views.banco_central_view, name='banco_central'),
]
