from django.urls import path
from django.contrib import admin

from .views import SchedulingListView, GetSchedulingDetailView
app_name = "app.schedulings"

urlpatterns = [
    path("", SchedulingListView.as_view(), name='list'),
    path('detail', GetSchedulingDetailView.as_view(), name='scheduling_detail')
]