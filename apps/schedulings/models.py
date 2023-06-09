from django.db import models
from django.conf import settings

# Create your models here.
class Scheduling(models.Model):
    employee_sid = models.IntegerField()
    date = models.DateField()
    shift_sid = models.IntegerField(null=True, blank=True)

    real_time_in = models.DateTimeField(null=True, blank=True)
    real_time_out = models.DateTimeField(null=True, blank=True)
    rest_time_in = models.DateTimeField(null=True, blank=True)
    rest_time_out = models.DateTimeField(null=True, blank=True)
    start_work_date_time = models.DateTimeField(null=True, blank=True)
    end_work_date_time = models.DateTimeField(null=True, blank=True)
    start_rest_date_time = models.DateTimeField(null=True, blank=True)
    end_rest_date_time = models.DateTimeField(null=True, blank=True)
    time_check_01 = models.DateTimeField(null=True, blank=True) 
    time_check_02 = models.DateTimeField(null=True, blank=True)
    time_check_03 = models.DateTimeField(null=True, blank=True)
    time_check_04 = models.DateTimeField(null=True, blank=True)
    time_check_05 = models.DateTimeField(null=True, blank=True)
    time_check_06 = models.DateTimeField(null=True, blank=True)
    time_check_07 = models.DateTimeField(null=True, blank=True)
    time_check_08 = models.DateTimeField(null=True, blank=True)
    time_check_09 = models.DateTimeField(null=True, blank=True)
    time_check_10 = models.DateTimeField(null=True, blank=True)
    time_check_11 = models.DateTimeField(null=True, blank=True)
    time_check_12 = models.DateTimeField(null=True, blank=True)
    time_check_13 = models.DateTimeField(null=True, blank=True)
    time_check_14 = models.DateTimeField(null=True, blank=True)
    time_check_15 = models.DateTimeField(null=True, blank=True)
    time_check_16 = models.DateTimeField(null=True, blank=True)
    is_holiday = models.BooleanField(default=False)
    holiday_from = models.DateTimeField(null=True, blank=True)
    holiday_to = models.DateTimeField(null=True, blank=True)
    holiday_name = models.CharField(max_length=255, null=True, blank=True)
    shift_name = models.CharField(max_length=25, null=True, blank=True)
    total_work_time = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    
    
    rest_shifts = models.BooleanField(default=False)
    fix_rest_time  = models.BooleanField(default=False)
    night = models.BooleanField(default=False)
    employee_code = models.CharField(max_length=25, null=True, blank=True)
    department_id = models.IntegerField(null=True, blank=True)
    name_employee = models.CharField(max_length=255, null=True, blank=True)
    job_title= models.CharField(max_length=255, null=True, blank=True)
    time_keeping_code= models.CharField(max_length=25, null=True, blank=True)
    department_name =models.CharField(max_length=255, null=True, blank=True)
    is_miss_in = models.BooleanField(default=False)
    is_miss_out = models.BooleanField(default=False)
    is_miss_in_mid = models.BooleanField(default=False)
    is_miss_out_mid = models.BooleanField(default=False)
    actual_work_time  = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    is_late_in = models.BooleanField(default=False)
    is_early_out = models.BooleanField(default=False)
    is_miss_one_mid = models.BooleanField(default=False)
    time_late_in  = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    time_early_out  = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    night_holiday_work_time  = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    night_work_time  = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    # MÃ NV MIS
    # NGÀY NHẬN VIỆC TẠI CÔNG TY
    date_join = models.DateField(null=True, blank= True)
    # THỜI GIAN THỬ VIỆC
    # THỬ VIỆC ĐẾN NGÀY
    probationary_to = models.DateField(null=True, blank= True)
    # SỐ HĐTV
    # NGÀY KÝ HĐLĐ LẦN 1
    # NGÀY HẾT HẠN HĐLĐ LẦN 1
    # SỐ HĐLĐ
    # Tỉ lệ hưởng lương TV
    is_probationary = models.BooleanField(default=False)
    scheduling_sid = models.IntegerField(null=True, blank=True)
    t_fist = models.DateTimeField(null=True, blank=True)
    t_last = models.DateTimeField(null=True, blank=True)
    list_type = models.TextField(null=True,blank=True)
    list_reason  = models.TextField(null=True,blank=True)

    class Meta:
        unique_together = ('employee_code', 'date')

