from django.shortcuts import render
from .models import Scheduling
from django.views.generic import ListView, View
import pandas as pd
from django.http import JsonResponse
# Create your views here.
from functools import reduce
def reducer(acc,el):
    group = el['department']
    if not acc.get(group):
        acc[group]=[el.get('name_employee')]
    else:
        acc[group].append(el['name_employee'])
    return acc
<<<<<<< HEAD


=======
class GetSchedulingDetailView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {
                # "asinid": self.asin_obj.id,
                "command": 1,
                'next_url': 1
            }
        )
>>>>>>> 3c97b8805264afe5efcd8ac8544724c860be7c1a
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
            Scheduling.objects.all().values_list('department_name', 'name_employee','employee_code', 'date', 'shift_name'))
        # print("11111",df)
        
        df['weekday'] = df.apply(lambda row:row[3].weekday(), axis=1)
        
        # print(df.head())
        results = []
        for g, data in df.groupby(0):
            group_data = []
            for g_code, data_code in data.groupby(2):
                fist_employee = data_code.iloc[0]
                item = {'department_name':g, 'name_employee': fist_employee[1], 'employee_code': g_code, 'D0':'', 'D1':'', 'D2':'', 'D3':'', 'D4':'', 'D5':'',  'D6':''}
                for sub_g, sub_data in data_code.groupby('weekday'):
                    fist_row = sub_data.iloc[0]
                    item['name_employee'] = fist_row[1]
                    item[f'D{sub_g}'] = fist_row[4]
                group_data.append(item)
            results.append({'department':g, 'data':group_data})
            print("dasdas",g)
        # print(queryset)
        context["schedulings"] = results
        # print(reduce(reducer, context["schedulings"], {}))
        # result = [{'department':'', 'data':[]}]
        # for scheduling in context["schedulings"]:

        #     departments = [d['department'] for d in result if d['department']==scheduling.department_name]
        #     if len(departments)>0:
        #         departments = departments
        return context
    
    