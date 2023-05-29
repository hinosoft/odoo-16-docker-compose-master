from django.shortcuts import render
from django.conf import settings
import xmlrpc.client
import pandas as pd

url = 'https://erp-test.apecgroup.net'
db = 'apecerp_sit'
username = 'hanhchinhnhansu'
password = '123123'


class OdooModel:
    # Create your vie`ws here.
    def odoo_get_list_employee(self):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.authenticate(db, username, password, {})
        # Check deparment
        department_ids = models.execute_kw(db, uid, password, 'hr.department','search', [[]])
        list_departments  = models.execute_kw(db, uid, password, 'hr.department', 'read', [department_ids], {'fields': ['id','name', 'total_employee', 'company_id', 'member_ids']})
        df_departments = pd.DataFrame.from_dict(list_departments)

        # read employee infomation
        employee_ids = models.execute_kw(db, uid, password, 'hr.employee', 'search', [[]])
        list_employees  = models.execute_kw(db, uid, password, 'hr.employee', 'read', [employee_ids], {'fields': ['id', 'name', 'user_id', 'company_id', 'code', 'department_id', 'time_keeping_code', 'job_title']})
        self.df_employees = pd.DataFrame.from_dict(list_employees)

        return list_employees



    

        