from django.test import TestCase
from apps.unities.views import SchedulingModel, AttendenceModel
# Create your tests here.

scheduling = SchedulingModel()
scheduling.sync_data_scheduling()

att = AttendenceModel()
att.append_tracking('C:/Users/HP/Documents/Github/black-dashboard-django-master/Apec-Convert-Data/unity/template/In/DLCC Mũi Né 16.5.23_full.xlsx')