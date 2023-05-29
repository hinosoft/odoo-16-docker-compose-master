from django.shortcuts import render
from .unity import HoaanhModel
# from .models import Emplyee
from rest_framework.views import APIView
from rest_framework.response import Response

class ProductCategory(APIView):
    """
    A simple ViewSet for listing or retrieving users.
    """
    # model = Emplyee 
    def get(self, request, format=None):
        model = HoaanhModel()
        queryset = model.odoo_get_product_public_category()
        return Response(queryset)
