from django.test import TestCase
from apps.unities.views import SchedulingModel, AttendenceModel
# Create your tests here.

scheduling = SchedulingModel()

scheduling.sync_data_scheduling()

# merge_infomation_to_d

att = AttendenceModel()
att.from_excel('C:/Users/Admin/Downloads/DLCC Mũi Né 16.5.23_full.xlsx')

scheduling.merge_download_attendance()
scheduling.merge_scheduling_ver()
scheduling.conver_data(None)