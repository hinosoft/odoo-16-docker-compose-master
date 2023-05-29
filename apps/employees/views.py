from django.shortcuts import render
from apps.unities.views import OdooModel
from .models import Emplyee
from rest_framework.views import APIView
from rest_framework.response import Response

class UserViewSet(APIView):
    """
    A simple ViewSet for listing or retrieving users.
    """
    model = Emplyee 
    def get(self, request, format=None):
        model = OdooModel()
        queryset = model.odoo_get_list_employee()
        return Response(queryset)
