from django.urls import path
from .views import UserViewSet
app_name = "apps.employees"
urlpatterns = [
    path("", UserViewSet.as_view(), name="vantaihahai_view"),
    
]