from django.db import models
from django.utils.translation import gettext_lazy as _


class JobStep(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    porcent = models.IntegerField(blank=False, null=False, db_index=True)

    class Meta:
        verbose_name = _('JobStep')
        verbose_name_plural = _('JobSteps')
        app_label = 'job'

    def Serialize(self):
        return {"id": self.pk,
                "name": self.name,
                "description": self.description,
                "porcent": self.porcent}


class job(models.Model):
    description = models.CharField(max_length=250, blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    end_date = models.DateTimeField(db_index=True, null=True)

    class Meta:
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')
        app_label = 'job'

    def Serialize(self):
        return {"id": self.pk,
                "description": self.description,
                "image": self.image,
                "jobStep": self.jobStep,
                "created_date": self.created_date,
                "end_date": self.end_date}


class JobHistory(models.Model):
    job = models.ForeignKey(job, on_delete=models.CASCADE)
    jobStep = models.ForeignKey(JobStep, on_delete=models.CASCADE)
    description = models.CharField(max_length=250, blank=True, null=True)
    start_Time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(db_index=True, null=True)
    actual = models.BooleanField(default=False, null=False)
    status = models.IntegerField(default=2, null=False)
    # 0 ERROR, 1 SUCCESS, 2 PROCESS, 3 CANCEL

    class Meta:
        verbose_name = _('JobHistory')
        verbose_name_plural = _('JobHistorys')
        app_label = 'job'

    def Serialize(self):
        status = "ERROR"
        if self.status == 1:
            status = "SUCCESS"
        if self.status == 2:
            status = "PROCESS"
        if self.status == 3:
            status = "CANCEL"

        return {"jobStep": self.jobStep.name,
                "status": status,
                "start_time": self.start_Time,
                "end_time": self.end_time}


class log(models.Model):
    process = models.CharField(max_length=250, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('JobLog')
        verbose_name_plural = _('JobLog')
        app_label = 'job'

    def Serialize(self):
        return {"process": self.process,
                "description": self.description,
                "date": self.date}
