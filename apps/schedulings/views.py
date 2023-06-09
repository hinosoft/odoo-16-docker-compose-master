from django.shortcuts import render
from .models import Scheduling
from django.views.generic import ListView
# Create your views here.

class SchedulingListView(ListView):
    model = Scheduling
    context_object_name = "schedulings"
    template_name = "home/schedulings.html"
    def get_queryset(self):
        # queryset = self.model.objects.all().select_related("account")
        queryset = self.model.objects.all()
        # if self.request.user.role != "ADMIN" and not self.request.user.is_superuser:
        #     queryset = queryset.filter(
        #         Q(created_by=self.request.user)
        #     )

        request_post = self.request.POST

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(SchedulingListView, self).get_context_data(**kwargs)
        context["schedulings"] = self.get_queryset()
        
        return context