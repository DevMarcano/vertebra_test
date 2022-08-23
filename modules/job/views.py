from modules.job.models import job, JobStep, JobHistory, log
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
import base64
from datetime import datetime
import io
from PIL import ImageChops, Image, ImageOps


def format_date(_date, action):
    if action == 0:
        return "%s 00:00:01" % (_date)
    else:
        return "%s 23:59:59" % (_date)


@api_view(['POST'])
def createJob(request):
    if 'image' in request.FILES:
        im = request.FILES['image'].read()
        print(im)
        img_base64 = base64.b64encode(im)
        image = img_base64.decode()
        print(image)
    else:
        newlog = log.objects.create(process="Create Job",
                                    description="Image not in request")
        newlog.save()
        return JsonResponse({"status": "error",
                             "message": "error al obtener la imagen"})

    step = JobStep.objects.get(pk=1)

    if 'description' in request.POST:
        description = request.POST['description']
    else:
        newlog = log.objects.create(process="Create Job",
                                    description="description not in request")
        newlog.save()
        return JsonResponse({"status": "error",
                             "message": "error al obtener la descripcion"})

    try:
        newJob = job.objects.create(description=description, image=image)
    except Exception as e:
        newlog = log.objects.create(process="Create Job",
                                    description=str(e))
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "error ocurred when create job"})
    newJob.save()
    try:
        newHistory = JobHistory.objects.create(job=newJob,
                                               jobStep=step,
                                               actual=1,
                                               status=2)
    except Exception as e:
        newJob.delete()
        newlog = log.objects.create(process="Create Job",
                                    description=str(e))
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "Error Save Job Step"})

    newHistory.save()
    return JsonResponse({"jobId": newJob.pk})


@api_view(['get'])
def getJob(request, pk):
    _gJob = job.objects.filter(pk=pk)
    if not _gJob.exists():
        newlog = log.objects.create(process="get Job",
                                    description="job dont exist")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "error job dont exist"})
    _gJob = _gJob[0]
    _stepHistory = JobHistory.objects.filter(job=pk)
    if not _stepHistory.exists():
        newlog = log.objects.create(process="get Job",
                                    description="error when get job step")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "error when get job step"})
    steps = []
    for data in _stepHistory:
        steps.append(data.Serialize())
    return JsonResponse(
            {"status": True,
             "jobid": _gJob.pk,
             "step": steps
             },
            status=200)


@api_view(['PUT'])
def succesStep(request):
    # succesStep se encarga de hacer el edit de las imagenes
    # y cambiar el estado de process a success
    if 'step' in request.data:
        _stepName = request.data['step']
    else:
        newlog = log.objects.create(process="update Job",
                                    description="not step in request")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "not step in request"})

    if 'jobId' in request.data:
        _jobId = request.data['jobId']
    else:
        newlog = log.objects.create(process="success step",
                                    description="not jobId in requets")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "not jobId in request"})

    _step = JobStep.objects.filter(name=_stepName)
    if not _step.exists():
        newlog = log.objects.create(process="success step",
                                    description="not aviable step")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": _stepName + " not aviable step"})
    _step = _step[0]

    _job = job.objects.filter(pk=_jobId)
    if not _job.exists():
        newlog = log.objects.create(process="success step",
                                    description=_jobId + " job dont exist")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": _jobId + " job dont exist"})
    _job = _job[0]
    try:
        _stateJob = JobHistory.objects.get(job=_job, jobStep=_step)

        # en caso de que no se requiera que se pueda repetir el step
        # if _stateJob.status == 1:
        #    return JsonResponse({"status": False,
        #                        "message": "step is already"})

        _currentStep = _stateJob.jobStep.name

        data = _job.image
        image = base64.b64decode(data)
        image2 = Image.open(io.BytesIO(image))
        if _currentStep == "Invertir los colores":
            inv_img = ImageChops.invert(image2)
            inv_img.save('new_name.png')
            _stateJob.status = 1
        if _currentStep == "Pasar a Blanco y Negro":
            bwImage = image2.convert('1')
            bwImage.save('new_name.png')
            _stateJob.status = 1
        if _currentStep == "Rotal la imagen 90 grados":
            im_rotate = image2.rotate(90)
            im_rotate.save('new_name.png')
            _stateJob.status = 1
        if (_currentStep == "Invertir sobre el eje vertical"):
            imgflip = ImageOps.flip(image2)
            imgflip.save('new_name.png')
            _stateJob.status = 1
        with open('new_name.png', 'rb') as f:
            byte_im = f.read()
        img_base64 = base64.b64encode(byte_im)
        _job.image = img_base64.decode()
        _job.save()
        _stateJob.end_time = datetime.now()
        _stateJob.save()

    except Exception as e:
        newlog = log.objects.create(process="success step",
                                    description=str(e))
        newlog.save()
        return JsonResponse({"status": False,
                             "message": str(e)})

    return JsonResponse({"status": True,
                         "message": "Proccess complete",
                         "jobid": _job.pk,
                         "step": _stateJob.Serialize()})


@api_view(['PUT'])
def updateJob(request):
    # update job se encarga de controlar el step actual del proceso
    if 'step' in request.data:
        _stepName = request.data['step']
    else:
        newlog = log.objects.create(process="update Job",
                                    description="not step in request")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "not step in request"})
    if 'jobId' in request.data:
        _jobId = request.data['jobId']
    else:
        newlog = log.objects.create(process="update Job",
                                    description="not jobId in request")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "not jobId in request"})

    _step = JobStep.objects.filter(name=_stepName)
    if not _step.exists():
        newlog = log.objects.create(process="update Job",
                                    description=_stepName + "is not available")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": _stepName + "is not step available"})
    _step = _step[0]

    _job = job.objects.filter(pk=_jobId)
    if not _job.exists():
        newlog = log.objects.create(process="update Job",
                                    description=_jobId + "this job dont exist")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": _jobId + "this job dont exist"})
    _job = _job[0]

    _stateJob = JobHistory.objects.get(job=_job, actual=1)
    if _stateJob.jobStep.pk == _step.pk:
        return JsonResponse({"status": False,
                             "message": "the job is already in this step"})

    _stateJob.actual = 0
    _stateJob.save()

    e_step = JobHistory.objects.filter(job=_job, jobStep=_step)
    if not e_step.exists():
        try:
            newHistory = JobHistory.objects.create(job=_job,
                                                   jobStep=_step,
                                                   actual=1,
                                                   status=2)
            e_step = newHistory
        except Exception as e:
            newlog = log.objects.create(process="update Job",
                                        description=str(e))
            newlog.save()
            return JsonResponse({"status": False,
                                "message": "create new step failed"})
    else:
        e_step = e_step[0]
        e_step.actual = 1
        e_step.save()
    return JsonResponse(
            {"status": True,
             "jobid": _job.pk,
             "step": e_step.Serialize()
             },
            status=200)


@api_view(['PUT'])
def endJob(request):
    # da por terminado el job colocando el end_date
    if 'jobId' in request.data:
        _jobId = request.data['jobId']
    else:
        newlog = log.objects.create(process="update Job",
                                    description="not jobId in request")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "not jobId in request"})
    _job = job.objects.filter(pk=_jobId)
    if not _job.exists():
        newlog = log.objects.create(process="update Job",
                                    description=_jobId + "this job dont exist")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": _jobId + "this job dont exist"})
    _job = _job[0]
    _job.end_date = datetime.now()
    _job.save()
    stepHistory = JobHistory.objects.filter(job=_job)
    steps = []
    for data in stepHistory:
        steps.append(data.Serialize())

    return JsonResponse({"status": True,
                         "message": "Job complete",
                         "job": _job.Serialize(),
                         "steps": steps})


@api_view(['get'])
def getLog(request):
    # get de los logs
    _inicio = request.GET['inicio']
    inicio = format_date(_inicio, 0)
    _final = request.GET['final']
    final = format_date(_final, 1)
    logs = log.objects.filter(date__range=(inicio, final))
    logsHistory = []
    if not logs.exists():
        newlog = log.objects.create(process="get logs",
                                    description="not logs in range date")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "not logs in range date"})
    for data in logs:
        logsHistory.append(data.Serialize())

    return JsonResponse({"logs": logsHistory})


# extras ya que son parecidos al de logs
# job created list in range date
@api_view(['get'])
def getJobsCreateDate(request):
    _inicio = request.GET['inicio']
    inicio = format_date(_inicio, 0)
    _final = request.GET['final']
    final = format_date(_final, 1)
    jobs = job.objects.filter(created_date__range=(inicio, final))
    jobsHistory = []
    for data in jobs:
        stepHistory = JobHistory.objects.filter(job=data.pk)
        steps = []
        for data in stepHistory:
            steps.append(data.Serialize())

        jobsHistory.append({"job": data.Serialize(), "step": steps})

    return JsonResponse({"jobs": jobsHistory})


# job end list in range date
@api_view(['get'])
def getJobsEndDate(request):
    _inicio = request.GET['inicio']
    inicio = format_date(_inicio, 0)
    _final = request.GET['final']
    final = format_date(_final, 1)
    jobs = job.objects.filter(end_date__range=(inicio, final))
    jobsHistory = []
    for data in jobs:
        stepHistory = JobHistory.objects.filter(job=data.pk)
        steps = []
        for data in stepHistory:
            steps.append(data.Serialize())

        jobsHistory.append({"job": data.Serialize(), "step": steps})

    return JsonResponse({"jobs": jobsHistory})
