from django.shortcuts import render
from django.conf import settings
import xmlrpc.client
import pandas as pd
from datetime import datetime
from datetime import timedelta
from apps.schedulings.models import Scheduling
from apps.attendences.models import Tracking

url = 'https://erp-test.apecgroup.net'
db = 'apecerp_sit'
username = 'hanhchinhnhansu'
password = '123123'
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def nearest(items, pivot):
    print('item vao')
    print(items)
    return pd.to_datetime(min([i for i in items if i <= pivot], key=lambda x: abs(x - pivot)))

def float_to_hours(float_time_hour):
    float_time = float_time_hour * 60  # in minutes
    hours, seconds = divmod(float_time * 60, 3600)  # split to hours and seconds
    minutes, seconds = divmod(seconds, 60)  # split the seconds to minutes and seconds
    return int(hours), int(minutes), int(seconds)

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
    
class SchedulingModel:
    def process_hour(self,row):
        return row['Giờ'].date()
    
    # ***************************************  SUMMARY REPORT ************************************
    def merge_download_attendance (self):
        # self.df_old = pd.read_excel(self.input_attendence_file , index_col=None, header=[0,] ,sheet_name='Sheet1')

        self.df_old  = pd.DataFrame.from_records(
            Tracking.objects.all().values_list('code', 'time'))
        self.df_old = self.df_old.set_axis(['ID', 'Giờ'], axis=1, copy=False)
        self.df_old['is_from_explanation'] = False

    def merge_scheduling_ver(self):
        self.date_array = pd.date_range(start='05/01/2023', end='05/31/2023')

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        self.uid = common.authenticate(db, username, password, {})
        
        # Check acess
        self.models.execute_kw(db, self.uid, password, 'res.partner', 'check_access_rights', ['read'], {'raise_exception': False})
        self.models.execute_kw(db, self.uid, password, 'res.partner', 'search', [[['is_company', '=', True]]])

        # Check deparment
        department_ids = self.models.execute_kw(db, self.uid, password, 'hr.department','search', [[]])
        list_departments  = self.models.execute_kw(db, self.uid, password, 'hr.department', 'read', [department_ids], {'fields': ['id','name', 'total_employee', 'company_id', 'member_ids']})
        df_departments = pd.DataFrame.from_dict(list_departments)


         # Check 'resource.calendar.leaves
        resource_calendar_leaves_ids = self.models.execute_kw(db, self.uid, password, 'resource.calendar.leaves','search', [[]])
        resource_calendar_leaves_list  = self.models.execute_kw(db, self.uid, password, 'resource.calendar.leaves', 'read', [resource_calendar_leaves_ids], \
                                                          {'fields': ['id','name', 'company_id', 'calendar_id', 'date_from', 'date_to', 'resource_id', 'time_type']})
        self.df_resource_calendar_leaves= pd.DataFrame.from_dict(resource_calendar_leaves_list)

        # read shift infomation
        ids = self.models.execute_kw(db, self.uid, password, 'shifts', 'search', [[]], {})
        list_shifts  = self.models.execute_kw(db, self.uid, password, 'shifts', 'read', [ids], {'fields': ['id', 'name', 'start_work_time', 'end_work_time','total_work_time','start_rest_time','end_rest_time','rest_shifts', 'fix_rest_time', 'night']})

        list_shifts.append({'id':-1, 'name':'-', 'start_work_time':12.00, 'end_work_time': 12.00, \
                'total_work_time':0.00,'start_rest_time':12.00,'end_rest_time':12.00,'rest_shifts':True, 'fix_rest_time':False, 'night':False})
        print (self.models.execute_kw(db, self.uid, password, 'shifts', 'fields_get', [], {'attributes': ['string', 'type']}))
        self.df_shift = pd.DataFrame.from_dict(list_shifts)
        # file_name = 'MarksData_df_shift.xlsx'
        # saving the excel
        # df_shift.to_excel(file_name)
        # print('DataFrame shift is written to Excel File successfully.')

   
        employee_Sids = self.models.execute_kw(db, self.uid, password, 'hr.employee', 'search', [[]])
        list_employees  = self.models.execute_kw(db, self.uid, password, 'hr.employee', 'read', [employee_Sids], {'fields': ['id', 'name', 'user_id', 'company_id', 'code', 'department_id', 'time_keeping_code', 'job_title']})
        # The above code is iterating through a list of employees and checking if their
        # 'time_keeping_code' attribute is not None. If it is not None, it removes the '.0' string
        # from the end of the attribute value using the replace() method.
        for employee in list_employees:
            if employee['time_keeping_code'] != None:
                employee['time_keeping_code'] = employee['time_keeping_code'].replace('.0', '')
        self.df_employees = pd.DataFrame.from_dict(list_employees)

        self.report_shift_ver  = pd.DataFrame.from_records(
            Scheduling.objects.all().values_list('department_name', 'date', 'start_work_date_time', 'end_work_date_time', 'start_rest_date_time',
                                                 'end_rest_date_time', 'employee_sid', 'name_employee', 'shift_name', 'shift_sid','fix_rest_time','night', 'rest_shifts', 'time_keeping_code'))
        self.report_shift_ver = self.report_shift_ver.set_axis(['department_name','date', 'start_work_date_time', 'end_work_date_time', 'start_rest_date_time',
                                                 'end_rest_date_time', 'employee_sid', 'name_employee', 'shift_name','shift', 'fix_rest_time', 'night','rest_shifts','time_keeping_code'], axis=1, copy=False)
        self.report_shift_ver['employee_id'] = self.report_shift_ver['employee_sid']
        self.calculate_normal_attendences_from_db()
        
        self.report_shift_ver['department_id']= self.report_shift_ver.apply(lambda row: ['',row['department_name']], axis=1)
        
        self.df_old['is_from_explanation'] = False


    def append_contract_data(self):
        df_attendance_data = pd.read_excel(self.input_contract_file_path, index_col=None, header= [0] ,sheet_name='Sheet1',
            converters={
                'THỬ VIỆC ĐẾN NGÀY': lambda x: pd.to_datetime(x, format='%d/%m/%Y',  errors='coerce'),
                'NGÀY NHẬN VIỆC TẠI CÔNG TY': lambda x: pd.to_datetime(x, format='%d/%m/%Y',  errors='coerce')
            })
        df_attendance_data =  df_attendance_data.drop_duplicates(subset=['MÃ NV MIS'], keep='first')
        
        self.report_shift_ver = self.report_shift_ver.merge(df_attendance_data[['MÃ NV MIS','NGÀY NHẬN VIỆC TẠI CÔNG TY', 'THỜI GIAN THỬ VIỆC', 'THỬ VIỆC ĐẾN NGÀY','SỐ HĐTV',
                'NGÀY KÝ HĐLĐ LẦN 1', 'NGÀY HẾT HẠN HĐLĐ LẦN 1', 'SỐ HĐLĐ', 'Tỉ lệ hưởng lương TV']], \
                left_on=['code'], right_on = ['MÃ NV MIS'], how='left', suffixes=( '' ,'_contract' ))
        
        self.report_shift_ver['is_probationary'] = self.report_shift_ver.apply(lambda x: (x['THỬ VIỆC ĐẾN NGÀY'] == None) or (pd.isnull(x['THỬ VIỆC ĐẾN NGÀY'])) or (x['date'] <= x['THỬ VIỆC ĐẾN NGÀY']), axis=1)

    def sync_data_scheduling(self):
        self.date_array = pd.date_range(start='05/01/2023', end='05/31/2023')

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        self.uid = common.authenticate(db, username, password, {})
        
        # Check acess
        self.models.execute_kw(db, self.uid, password, 'res.partner', 'check_access_rights', ['read'], {'raise_exception': False})
        self.models.execute_kw(db, self.uid, password, 'res.partner', 'search', [[['is_company', '=', True]]])

        # Check deparment
        department_ids = self.models.execute_kw(db, self.uid, password, 'hr.department','search', [[]])
        list_departments  = self.models.execute_kw(db, self.uid, password, 'hr.department', 'read', [department_ids], {'fields': ['id','name', 'total_employee', 'company_id', 'member_ids']})
        df_departments = pd.DataFrame.from_dict(list_departments)


         # Check 'resource.calendar.leaves
        resource_calendar_leaves_ids = self.models.execute_kw(db, self.uid, password, 'resource.calendar.leaves','search', [[]])
        resource_calendar_leaves_list  = self.models.execute_kw(db, self.uid, password, 'resource.calendar.leaves', 'read', [resource_calendar_leaves_ids], \
                                                          {'fields': ['id','name', 'company_id', 'calendar_id', 'date_from', 'date_to', 'resource_id', 'time_type']})
        self.df_resource_calendar_leaves= pd.DataFrame.from_dict(resource_calendar_leaves_list)

        # read shift infomation
        ids = self.models.execute_kw(db, self.uid, password, 'shifts', 'search', [[]], {})
        list_shifts  = self.models.execute_kw(db, self.uid, password, 'shifts', 'read', [ids], {'fields': ['id', 'name', 'start_work_time', 'end_work_time','total_work_time','start_rest_time','end_rest_time','rest_shifts', 'fix_rest_time', 'night']})

        list_shifts.append({'id':-1, 'name':'-', 'start_work_time':12.00, 'end_work_time': 12.00, \
                'total_work_time':0.00,'start_rest_time':12.00,'end_rest_time':12.00,'rest_shifts':True, 'fix_rest_time':False, 'night':False})
        print (self.models.execute_kw(db, self.uid, password, 'shifts', 'fields_get', [], {'attributes': ['string', 'type']}))
        self.df_shift = pd.DataFrame.from_dict(list_shifts)
        # file_name = 'MarksData_df_shift.xlsx'
        # saving the excel
        # df_shift.to_excel(file_name)
        # print('DataFrame shift is written to Excel File successfully.')

   
        employee_Sids = self.models.execute_kw(db, self.uid, password, 'hr.employee', 'search', [[]])
        list_employees  = self.models.execute_kw(db, self.uid, password, 'hr.employee', 'read', [employee_Sids], {'fields': ['id', 'name', 'user_id', 'company_id', 'code', 'department_id', 'time_keeping_code', 'job_title']})
        # The above code is iterating through a list of employees and checking if their
        # 'time_keeping_code' attribute is not None. If it is not None, it removes the '.0' string
        # from the end of the attribute value using the replace() method.
        for employee in list_employees:
            if employee['time_keeping_code'] != None:
                employee['time_keeping_code'] = employee['time_keeping_code'].replace('.0', '')
        self.df_employees = pd.DataFrame.from_dict(list_employees)
        

        explanation_ids = self.models.execute_kw(db, self.uid, password,'hr.invalid.timesheet', 'search',  [[]])
        list_old_explanation = self.models.execute_kw(db, self.uid, password, 'hr.invalid.timesheet', 'read', [explanation_ids], {'fields': ['id', 'employee_id', 'employee_code', 'department', \
                                                                                                                            'position', 'invalid_date', 'invalid_type', 'shift_from', 'shift_to', 'shift_break', 'real_time_attendance_data', \
                                                                                                                    'validated', 'reason', 'reason', 'remarks','validation_data' ]})
        if len(list_old_explanation)>0: 
            self.df_explanation_data = pd.DataFrame.from_dict(list_old_explanation)
        else:
            self.df_explanation_data = pd.DataFrame(columns= ['id', 'employee_id', 'employee_code', 'department', \
                                                                'position', 'invalid_date', 'invalid_type', 'shift_from', 'shift_to', 'shift_break', 'real_time_attendance_data', \
                                                                'validated', 'reason', 'reason', 'remarks','validation_data','date_str', 'Lý do', 'Invalid Type'])
    
        
       
        # self.date_array = pd.date_range(start='05/01/2023', end='05/31/2023')
        print (self.date_array)
        start_str = self.date_array[0].strftime('%Y-%m-%d')
        end_str = self.date_array[len(self.date_array)-1].strftime('%Y-%m-%d')
        scheduling_ids = self.models.execute_kw(db, self.uid, password, 'employees_scheduling', 'search', [["|", 
                "&",("stop", ">=", start_str),("stop", "<=", end_str),
                "&",("start", ">=", start_str),("start", "<=", end_str)]], {})
        list_scheduling  = self.models.execute_kw(db, self.uid, password, 'employees_scheduling', 'read', [scheduling_ids], {'fields': [ 'id', 'start', 'stop','shift_monday', 'shift_tuesday','shift_wednesday','shift_thursday','shift_friday','shift_saturday', 'shift_sunday','employee_ids']})
        self.df_scheduling = pd.DataFrame.from_dict(list_scheduling)
        self.df_scheduling.set_index('id')
        ver_results = []
        
        for scheduling in list_scheduling:
            start_date = scheduling['start']
            end_date = scheduling['stop']
            employee_ids = scheduling['employee_ids']
            date_range = pd.date_range(start=start_date ,end= end_date)
            for item in date_range:
                # print("new", item.strftime("%d_%m"))
                item_weekday = item.weekday()
                found = False
                for item_date_array in self.date_array:
                    if item == item_date_array:
                        found = True
                if not found:
                    print('add: ', item.strftime("%y_%d_%m"))
                    self.date_array.append(item)

                # print('{}-{}'.format(item.weekday(),item))
                item_shifts = []
                if item_weekday == 0:
                    item_shifts = scheduling['shift_monday']
                elif item_weekday == 1:
                    item_shifts = scheduling['shift_tuesday']
                elif item_weekday == 2:
                    item_shifts = scheduling['shift_wednesday']
                elif item_weekday == 3:
                    item_shifts = scheduling['shift_thursday']
                elif item_weekday == 4:
                    item_shifts = scheduling['shift_friday']
                elif item_weekday == 5:
                    item_shifts = scheduling['shift_saturday']
                elif item_weekday == 6:
                    item_shifts = scheduling['shift_sunday']

                for shift in item_shifts:
                    for employee_id in employee_ids:
                        # find employee in results
                        # find_item = None
                        # for result_item in results:
                        #     if result_item['employee_id'] == employee_id:
                        #         find_item = result_item
                        #         break
                        # if not find_item:
                        find_item = {'employee_id': employee_id, 'date': item,'shift':shift, 'real_time_in': None, 'real_time_out': None, 
                            'rest_time_in': None, 'rest_time_out': None, 'max_time_in': None, 'min_time_out':None, \
                            'scheduling_start': date_range[0], 'scheduling_end':date_range[len(date_range)-1],
                            'start_work_date_time': None, 'end_work_date_time':None, 'start_rest_date_time': None, 'end_rest_date_time':None,
                            'normal_checks':[], 'is_holiday': False, 'holiday_from': None, 'holiday_to': None, 'holiday_name': '', 'server_id': scheduling['id']}
                        #     results.append(find_item)
                        # find_item[item] = shift
                        ver_results.append(find_item)

        for employee_id in employee_Sids:
            for date_item in self.date_array:
                scheduling_start = date_item
                scheduling_end = date_item
                if len([x for x in ver_results if x['date']== date_item and x['employee_id'] == employee_id]) == 0:
                    # print(" Append blank item ")
                    # date = row['date']
                    server_id = -1
                    for item in list_scheduling:
                        if (employee_id in item['employee_ids']):
                            date_range = pd.date_range(start=item['start'], end=item['stop'])
                            print(date_range)

                            if (date_item in date_range):
                                server_id =  item['id']
                                scheduling_start = date_range[0]
                                scheduling_end = date_range[len(date_range)-1]
                                

                    find_item = {'employee_id': employee_id, 'date': date_item,'shift':-1, 'real_time_in': None, 'real_time_out': None, 
                            'rest_time_in': None, 'rest_time_out': None, 'max_time_in': None, 'min_time_out':None,
                            'scheduling_start': scheduling_start, 'scheduling_end':scheduling_end,
                            'start_work_date_time': None, 'end_work_date_time':None, 'start_rest_date_time': None, 'end_rest_date_time':None,
                            'normal_checks':[], 'is_holiday': False, 'holiday_from': None, 'holiday_to': None, 'holiday_name': '', 'server_id':server_id}
                    
                    ver_results.append(find_item)

    
        self.report_shift_ver  = pd.DataFrame.from_dict(ver_results)
        self.report_shift_ver =  self.report_shift_ver.merge(self.df_shift[['id','name', 'total_work_time','start_work_time','end_work_time','rest_shifts', 'start_rest_time','end_rest_time', 'fix_rest_time', 'night']], 
                    left_on=['shift'], right_on = ['id'], how='left', suffixes=( '' ,'_y')).drop(['id'], axis=1)
        # self.report_shift_ver.index = np.arange(1, len(self.report_shift_ver)+ 1)

        self.calculate_normal_attendences()
        print("*********************MERGE HOLYDAY*********************")
        self.merge_calendar_leaves()
        self.df_normal_attendances[['is_holiday', 'holiday_from', 'holiday_to', 'holiday_name']] = \
            self.df_normal_attendances.apply(lambda row: self.merge_holiday(row), axis=1, result_type='expand')

        # merge employee
        self.report_shift_ver =  self.report_shift_ver.merge(self.df_employees[['id','code', 'department_id', 'name','job_title','time_keeping_code']], left_on=['employee_id'], right_on = ['id'], how='left', suffixes=( '' ,'_employee' ))
        self.report_shift_ver.rename(columns = {'id':'employee_sid'}, inplace = True)
        # Import to db 
        self.report_shift_ver.apply(lambda row: self.update_report_scheduling_db(row), axis=1)
    def calculate_normal_attendences_from_db(self):
        normal_attendances = []
        for index, row in self.report_shift_ver.iterrows():
            

            start_work_date_time = row['start_work_date_time']
            end_work_date_time =  row['end_work_date_time']

            

            normal_attendances.append({"employee_id": row['employee_id'], 'shift':row['shift'], 'shift_name':row['shift_name'], 'time':start_work_date_time, 'scheduling': index, 
                        'rest_shifts':row['rest_shifts'],'fix_rest_time': row['fix_rest_time'], 'night':row['night'],'label': 'In' }, time_keeping_code = int(row['time_keeping_code']))
            normal_attendances.append({"employee_id": row['employee_id'], 'shift':row['shift'], 'shift_name':row['shift_name'], 'time':end_work_date_time, 'scheduling': index, 
                        'rest_shifts':row['rest_shifts'],'fix_rest_time': row['fix_rest_time'], 'night':row['night'],'label': 'Out' }, time_keeping_code = int(row['time_keeping_code']))

            
        self.df_normal_attendances = pd.DataFrame.from_dict(normal_attendances)
        print("*********************MERGE HOLYDAY*********************")
        self.merge_calendar_leaves()
        self.df_normal_attendances[['is_holiday', 'holiday_from', 'holiday_to', 'holiday_name']] = \
            self.df_normal_attendances.apply(lambda row: self.merge_holiday(row), axis=1, result_type='expand')
    def calculate_normal_attendences(self):
        normal_attendances = []
        for index, row in self.report_shift_ver.iterrows():
            start_work_time_h, start_work_time_m,start_work_time_s = float_to_hours (row['start_work_time'])
            end_work_time_h, end_work_time_m, end_work_time_s= float_to_hours (row['end_work_time'])

            print('{}-{}'.format(row['start_work_time'], row['end_work_time']))
            end_work_date = row['date']
            if row['start_work_time'] > row['end_work_time']:
                end_work_date = row['date'] + timedelta(days=1)

            start_work_date_time = row['date'].replace(hour=start_work_time_h, minute=start_work_time_m, second=0)
            end_work_date_time =  end_work_date.replace(hour=end_work_time_h, minute=end_work_time_m, second=0)

            start_rest_date = row['date'] + timedelta(days=1) if row['start_work_time'] > row['start_rest_time'] else row['date'] 
            end_rest_date = row['date'] + timedelta(days=1) if row['start_work_time'] > row['end_rest_time'] else row['date'] 

            start_rest_time_h, start_rest_time_m,start_rest_time_s = float_to_hours (row['start_rest_time'])
            end_rest_time_h, end_rest_time_m, end_rest_time_s = float_to_hours (row['end_rest_time'])

            start_rest_date_time = start_rest_date.replace(hour=start_rest_time_h, minute=start_rest_time_m, second=0)
            end_rest_date_time = end_rest_date.replace(hour=end_rest_time_h, minute=end_rest_time_m, second=0)

            normal_attendances.append({"employee_id": row['employee_id'], 'shift':row['shift'], 'shift_name':row['name'], 'time':start_work_date_time, 'scheduling': index, 
                        'rest_shifts':row['rest_shifts'],'fix_rest_time':row['fix_rest_time'], 'night':row['night'],'label': 'In'})
            normal_attendances.append({"employee_id": row['employee_id'], 'shift':row['shift'], 'shift_name':row['name'], 'time':end_work_date_time, 'scheduling': index, 
                        'rest_shifts':row['rest_shifts'],'fix_rest_time':row['fix_rest_time'], 'night':row['night'],'label': 'Out'})

            if row['fix_rest_time']:
                normal_attendances.append({"employee_id": row['employee_id'], 'shift':row['shift'], 'shift_name':row['name'], 'time':start_rest_date_time, 'scheduling': index, 
                        'rest_shifts':row['rest_shifts'],'fix_rest_time': row['fix_rest_time'], 'night':row['night'], 'label': 'Out-Mid'})

                normal_attendances.append({"employee_id": row['employee_id'], 'shift':row['shift'], 'shift_name':row['name'], 'time':end_rest_date_time, 'scheduling': index, 
                        'rest_shifts':row['rest_shifts'],'fix_rest_time':row['fix_rest_time'], 'night':row['night'], 'label': 'In-Mid'})
            self.report_shift_ver.at[index,'start_work_date_time'] = start_work_date_time
            self.report_shift_ver.at[index,'end_work_date_time'] = end_work_date_time

            self.report_shift_ver.at[index,'start_rest_date_time'] = start_rest_date_time
            self.report_shift_ver.at[index,'end_rest_date_time'] = end_rest_date_time
        self.df_normal_attendances = pd.DataFrame.from_dict(normal_attendances)
    ########################### 'resource.calendar.leaves
    def merge_holiday(self, row):
        is_holiday = False
        holiday_from = None
        holiday_to = None
        holiday_name = ''
        try:
            shift_time = row['time']
            df_compare = self.df_resource_calendar_leaves[(self.df_resource_calendar_leaves['date_from']<=shift_time) & \
                                            (self.df_resource_calendar_leaves['date_to']>=shift_time)]
            
            if len(df_compare.index) > 0:
                fist_row = df_compare.iloc[0]
                is_holiday = True
                holiday_from = fist_row['date_from']
                holiday_to = fist_row['date_to']
                holiday_name = fist_row['name']

        except Exception as ex:
            is_holiday = False

            print('merge error: ', ex)
            
        return is_holiday, holiday_from, holiday_to, holiday_name
    def refact_date_from(self, row):
        date_from = row['date_from']
        print('date {} from {}'.format (date_from, type(date_from)))
        try:
            date_from =  datetime.datetime.strptime(row['date_from'],'%Y-%m-%d %H:%M:%S').replace(hour=0,minute=0,second=0)
        except Exception as ex:
            print (ex)
        date_to = row['date_to']
        try:
            date_to =  datetime.datetime.strptime(row['date_to'], '%Y-%m-%d %H:%M:%S').replace(hour=0,minute=0,second=0)
            date_to = date_to + datetime.timedelta(days=1)
        except Exception as ex:
            print ('date_to', ex)
        return date_from, date_to
    
    def merge_calendar_leaves(self):

        print('***************CALENDAR************************************')
        
        self.df_resource_calendar_leaves[['date_from', 'date_to']]= self.df_resource_calendar_leaves.apply(lambda row: self.refact_date_from(row), axis=1, result_type='expand')
        # self.df_resource_calendar_leaves['date_to']=self.df_resource_calendar_leaves.apply(lambda row: row['date_to'].replace(hour=23,minute=59,second=59), axis=1)
        print(self.df_resource_calendar_leaves)
    
    def update_report_scheduling_db(self,row):

        scheduling_date = row['date']
        scheduling_emloyee_name = row['name_employee']
        scheduling_shift_name = row['name']
        employee_code = row['code']
        department_id = row['department_id']
        employee_sid = row['employee_sid']
        start_work_date_time = row['start_work_date_time']
        end_work_date_time = row['end_work_date_time']
        start_rest_date_time = row['start_rest_date_time']
        end_rest_date_time = row['end_rest_date_time']
        shift_id = row['shift']
        fix_rest_time = row['fix_rest_time']
        night = row['night']
        rest_shifts = row['rest_shifts'] 
        time_keeping_code = row['time_keeping_code']
        try:
            scheduling_object = Scheduling.objects.get(employee_code = employee_code, date=scheduling_date)
            
            # scheduling_object.save()   
        except:
            scheduling_object = Scheduling(employee_code = employee_code, date=scheduling_date)
        department_name = ''
        if department_id:
            if len(department_id) > 1:
                department_name = department_id[1]
        scheduling_object.department_name = department_name
        scheduling_object.start_work_date_time = start_work_date_time
        scheduling_object.end_work_date_time = end_work_date_time
        scheduling_object.start_rest_date_time = start_rest_date_time
        scheduling_object.end_rest_date_time = end_rest_date_time
        scheduling_object.employee_sid = employee_sid if employee_sid else -1
        scheduling_object.name_employee = scheduling_emloyee_name
        scheduling_object.shift_name = scheduling_shift_name
        scheduling_object.shift_sid = shift_id
        scheduling_object.fix_rest_time = fix_rest_time
        scheduling_object.night = night
        scheduling_object.rest_shifts = rest_shifts
        scheduling_object.time_keeping_code = time_keeping_code
        scheduling_object.save()   
        

    def find_nearest(self, row):
        # print(self.df_normal_attendances['employee_id'])
        # print(row['employee_id'])
        is_holiday = False
        holiday_from = None
        holiday_to = None
        holiday_name = ''
        shift = 0
        shift_id = 0
        normal_time = 0
        rest_shifts = False
        fix_rest_time = False
        night = False
        label = ''
        scheduling = -1
        try: 
            df_compare = self.df_normal_attendances[self.df_normal_attendances['time_keeping_code']==row['id']].sort_values(by=['time'])
            if len(df_compare['time'])>0:
                dates = df_compare['time'].to_list()
                min_time = min(dates, key=lambda d: abs(d-row['Giờ']))
                # print('min: ', min_time)
                # normal_shift_row = df_compare.iloc[df_compare['time'].get_loc(row['Giờ'],method='nearest')]
                # print(df_compare['time'].searchsorted(row['Giờ']))
                normal_shift_row = df_compare[df_compare['time']==min_time].iloc[0]
                scheduling = normal_shift_row['scheduling']

                shift = normal_shift_row['shift_name']
                shift_id = normal_shift_row['shift']
                normal_time = normal_shift_row['time']
                
                rest_shifts = normal_shift_row['rest_shifts']
                fix_rest_time = normal_shift_row['fix_rest_time']
                night = normal_shift_row['night']
                if fix_rest_time:
                    print("cooooooooooooooooooooooooooooo")
                label = normal_shift_row['label']
                is_holiday = normal_shift_row['is_holiday']
                holiday_from = normal_shift_row['holiday_from']
                holiday_to = normal_shift_row['holiday_to']
                holiday_name = normal_shift_row['holiday_name']
                # self.report_shift_ver.at[scheduling,'t_array'].append(row['Giờ'])
            # return shift, shift_id, normal_time, scheduling, rest_shifts, fix_rest_time, night ,label, is_holiday, holiday_from, holiday_to, holiday_name
        except Exception as ex:
            print('Find nearest errrrrrrrrr: ', ex)
            
            
        return shift, shift_id, normal_time, scheduling, rest_shifts, fix_rest_time, night, label,  is_holiday, holiday_from, holiday_to, holiday_name
    
    def convert_scheduling_date(self, row):
        result = '-'
        if pd.notnull( row['date']):
            date_str = row['date'].strftime('%Y_%m_%d')   
            result = date_str
        
        return result   
    def merge_infomation_to_df(self):
        """
        Merge information to dfver
        column t1, t2, t3,... t10, t_fist, t_last

        """
        self.df_attendence_group = self.df_old[~self.df_old['is_from_explanation']].sort_values(['Giờ']).groupby('scheduling')
        result = []
        for g, data in self.df_attendence_group:
            t_fist = None
            t_last = None
            t_mid_array = []
            t_fist = data.iloc[0]['Giờ']
            len_df = len(data['Giờ'])
            if (len_df > 1):
                t_last = data.iloc[len_df -1]['Giờ']
            for item in data['Giờ']:
                if item != t_fist and item != t_last:
                    t_mid_array.append (item)
            result_item = {'scheduling': g, 't_fist': t_fist, 't_last': t_last, 't_mid_array': t_mid_array}

            result.append(result_item)

        self.df_attendence_hor= pd.DataFrame.from_dict(result)

        self.report_shift_ver = self.report_shift_ver.merge(self.df_attendence_hor, left_index=True, right_on = ['scheduling'], how='left')
        # self.report_shift_ver.to_excel(os.path.join(self.output_report_folder, 'convitso6.xlsx'), sheet_name='Sheet1') 

        # merge self.df_attendance_data
        self.report_shift_ver['date_str'] = self.report_shift_ver.apply(lambda row: self.convert_scheduling_date(row), axis=1, result_type='expand')
        
        # self.report_shift_ver = self.report_shift_ver.merge(self.append_explanation_data_collect, left_on=['code','date_str'], right_on=['Employee ID','date_str'], how='left')


    def conver_data_from_db(self, progress_callback=None):
        # self.report_shift_ver['t_array'] = []
        # if not self.is_prepared_data:
        # self.df_employees['time_keeping_code'] = pd.to_numeric(self.df_employees['time_keeping_code'], errors='coerce')
        self.df_normal_attendances['time_keeping_code'] = pd.to_numeric(self.df_normal_attendances['time_keeping_code'], errors='coerce')
        # self.df_old = self.df_old.merge(self.df_employees[['id','code', 'department_id', 'name','time_keeping_code','job_title']], \
        #         left_on=['ID'], right_on = ['time_keeping_code'], how='left', suffixes=( '' ,'_employee' ))
        # self.df_old .rename(columns={'id': 'employee_id'})
        # self.df_old.to_excel("atempbc.xlsx", sheet_name='Sheet1') 
        self.df_old['yearmonth']=self.df_old.apply(lambda row: self.process_hour(row), axis=1, result_type='expand') 
        # self.df_old.to_excel(self.output_file, sheet_name='Sheet1') 
        self.df_old[['shift_name', 'shift_id', 'normal_time', 'scheduling', 'rest_shifts', 'fix_rest_time', 'night' , 'label', \
            'is_holiday', 'holiday_from', 'holiday_to', 'holiday_name']] = \
            self.df_old.apply(lambda row: self.find_nearest(row), axis=1, result_type='expand') 
        
        self.merge_infomation_to_df()
        # df_sort = self.df_old.sort_values(by=['ID', 'Giờ'], ascending=False)
        # self.result = df_sort.groupby(['ID', 'scheduling']).agg({'Giờ': ['mean', 'min', 'max']})
        # # self.df_old["In/out"] = self.df_old.apply(lambda row: self.process_content(row), axis=1, result_type='expand') 

        # df_mid_sort = self.df_old[(self.df_old["label"]=='In-Mid')].sort_values(by=['ID', 'Giờ'], ascending=False)
        # self.df_in_mid_result = df_mid_sort.groupby(['ID', 'scheduling']).agg({'Giờ': ['mean', 'min', 'max']})

        # df_mid_sort = self.df_old[(self.df_old["label"]=='Out-Mid')].sort_values(by=['ID', 'Giờ'], ascending=False)
        # self.df_out_mid_result = df_mid_sort.groupby(['ID', 'scheduling']).agg({'Giờ': ['mean', 'min', 'max']})

        # # find max time in and min timeout
        # df_attendence_group = self.df_old[~self.df_old['is_from_explanation']].sort_values(['Giờ']).groupby('scheduling')
        # # result = []
        # for g, data in df_attendence_group:
        #     t_fist = None
        #     t_last = None
        #     t_mid_array = []
        #     t_fist = data.iloc[0]['Giờ']
        #     len_df = len(data['Giờ'])
        #     if (len_df > 1):
        #         t_last = data.iloc[len_df -1]['Giờ']
        #     for item in data['Giờ']:
        #         if item != t_fist and item != t_last:
        #             t_mid_array.append (item)

        #     # result_item = {'scheduling': g, 't_fist': t_fist, 't_last': t_last, 't_mid_array': t_mid_array}
        #     # result.append(result_item)
        #     if g>=0:
        #         max_time_in = t_fist
        #         try:
        #             if max_time_in != None and  max_time_in.replace(second=0) < self.report_shift_ver['start_work_date_time'][g]:
        #                 max_time_in = max([a for a in data['Giờ'] if a.replace(second=0) <= self.report_shift_ver['start_work_date_time'][g]])
        #         except:
        #             self.report_shift_ver.to_excel('nho ti ti.xlsx')
        #         min_time_out = t_last
        #         try:
        #             if min_time_out != None and  min_time_out.replace(second=0) > self.report_shift_ver['end_work_date_time'][g]:
        #                 min_time_out = min ([a for a in data['Giờ'] if a.replace(second=0) >= self.report_shift_ver['end_work_date_time'][g]])
        #         except:
        #             self.df_old.to_excel('Hoi kho nhi.xlsx')

        #         self.report_shift_ver.at[g, 'min_time_out'] = min_time_out
        #         self.report_shift_ver.at[g, 'max_time_in'] = max_time_in

            
        # # Cai nay tu tu thay duoc
        # self.df_old["In/out"] = self.df_old.apply(lambda row: self.process_content(row), axis=1, result_type='expand') 
        print("Mean, min, and max values of Top Speed grouped by Vehicle Type")
       
        

class AttendenceModel:
    def from_excel(self, file_path):
        df_old = pd.read_excel(file_path , index_col=None, header=[0,] ,sheet_name='Sheet1')
        df_old.apply(lambda row: self.append_tracking(row), axis=1)
    def append_tracking(self, row):
        # print('----------',row['ID'])
        code = row['ID']
        time = row['Giờ']
        try:
            tracking = Tracking(code= code, time= time)
            tracking.save()
        except Exception as ex:
            print("tracking", ex)




