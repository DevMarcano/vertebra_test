from django.urls import re_path as url
from modules.job import views as job_view

urlpatterns = [
    url(r'^createjob/$', job_view.createJob),
    url(r'^getjob/(?P<pk>[\w-]+)$', job_view.getJob),
    url(r'^updateprocess', job_view.updateJob),
    url(r'^successstep', job_view.succesStep),
    url(r'^loghistory', job_view.getLog),
    url(r'^jobscreateindate', job_view.getJobsCreateDate),
    url(r'^jobsendindate', job_view.getJobsEndDate),
    url(r'^endjob', job_view.endJob)
]
