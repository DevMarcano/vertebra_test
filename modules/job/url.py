from django.urls import re_path as url
from modules.job import views as job_view

urlpatterns = [
    url(r'^createjob/$', job_view.createJob),
    url(r'^getjob/(?P<pk>[\w-]+)$', job_view.getJob),
    url(r'^updateimage', job_view.updateJob),
    url(r'^loghistory', job_view.getLog),
]
