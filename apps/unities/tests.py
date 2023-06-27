from django.test import TestCase
from apps.unities.views import SchedulingModel, AttendenceModel
# Create your tests here.

scheduling = SchedulingModel()

scheduling.sync_data_scheduling()

# merge_infomation_to_d

att = AttendenceModel()
att.from_excel('C:/Users/Admin/Desktop/Mũi Né 1-20.6.xlsx')

scheduling.merge_download_attendance()
scheduling.merge_scheduling_ver()
scheduling.conver_data(None)