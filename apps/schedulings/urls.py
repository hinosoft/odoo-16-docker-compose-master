from django.urls import path
from django.contrib import admin

from .views import SchedulingListView
app_name = "app.schedulings"

urlpatterns = [
    path("", SchedulingListView.as_view(), name='list'),
]