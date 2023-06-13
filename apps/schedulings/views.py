from django.shortcuts import render
from .models import Scheduling
from django.views.generic import ListView
import pandas as pd

# Create your views here.
from functools import reduce
def reducer(acc,el):
    group = el['department']
    if not acc.get(group):
        acc[group]=[el.get('name_employee')]
    else:
        acc[group].append(el['name_employee'])
    return acc

class SchedulingListView(ListView):
    model = Scheduling
    context_object_name = "schedulings"
    template_name = "home/schedulings.html"
    def get_queryset(self):
        # queryset = self.model.objects.all().select_related("account")
        results = []
        queryset = self.model.objects.all()
        
        # if self.request.user.role != "ADMIN" and not self.request.user.is_superuser:
        #     queryset = queryset.filter(
        #         Q(created_by=self.request.user)
        #     )

        request_post = self.request.POST

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(SchedulingListView, self).get_context_data(**kwargs)
        # df = pd.DataFrame.from_records(self.get_queryset())
        df = pd.DataFrame.from_records(
            Scheduling.objects.all().values_list('department_name', 'name_employee','employee_code', 'date', 'shift_name'),
            columns=['department_name', 'name_employee','employee_code', 'date', 'shift_name'])
        print("11111",(df.columns))
        
        df['weekday'] = df['date'].apply(lambda row:row[3].weekday(), axis=1)
        # df['weekday'] = pd.Series(df['date']).apply(lambda row: row[3].weekday())
        # df['weekday'] = df['date'].apply(lambda row: row[3].weekday())
        
        # print(df.head())
        results = []
        for g, data in df.groupby('department_name'):
            group_data = []
            for g_code, data_code in data.groupby('employee_code'):
                fist_employee = data_code.iloc['department_name']
                item = {'department_name':g, 'name_employee': fist_employee[1], 'employee_code': g_code, 'D0':'', 'D1':'', 'D2':'', 'D3':'', 'D4':'', 'D5':'',  'D6':''}
                for sub_g, sub_data in data_code.groupby('weekday'):
                    fist_row = sub_data.iloc['department_name']
                    item['name_employee'] = fist_row['name_employee']
                    item[f'D{sub_g}'] = fist_row['shift_name']
                group_data.append(item)
            results.append({'department':g, 'data':group_data})
            print(g)
        # print(queryset)
        context["schedulings"] = results
        # print(reduce(reducer, context["schedulings"], {}))
        # result = [{'department':'', 'data':[]}]
        # for scheduling in context["schedulings"]:

        #     departments = [d['department'] for d in result if d['department']==scheduling.department_name]
        #     if len(departments)>0:
        #         departments = departments
        return context