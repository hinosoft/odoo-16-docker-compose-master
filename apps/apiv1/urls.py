from django.urls import path
from .views import ProductCategory
app_name = "apps.apiv1"
urlpatterns = [
    path("categories", ProductCategory.as_view(), name="list_category_view"), 
]