from django.urls import re_path as url
from django.conf.urls import include

urlpatterns = [   
    url(r'^api/v1/job/', include('modules.job.url')),
]
