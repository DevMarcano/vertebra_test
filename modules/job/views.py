from modules.job.models import job, JobStep, JobHistory, log
from django.http.response import JsonResponse
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view
import base64
from datetime import datetime
# import cv2


def format_date(_date, action):
    if action == 0:
        return "%s 00:00:01" % (_date)
    else:
        return "%s 23:59:59" % (_date)


@api_view(['POST'])
def createJob(request):
    if 'image' in request.FILES:
        im_b64 = request.FILES['image']
        img_bytes = base64.b64decode(str(im_b64))
        image = img_bytes  # request.FILES['image']
    else:
        newlog = log.objects.create(process="Create Job",
                                    description="Image not in request")
        newlog.save()
        return JsonResponse({"status": "error",
                             "message": "error al obtener la imagen"},
                            status=500)

    step = JobStep.objects.get(pk=1)
    description = request.POST['description']
    try:
        newJob = job.objects.create(description=description, image=str(image))
    except:
        newlog = log.objects.create(process="Create Job",
                                    description="Error Save Job")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "error ocurred when create job"})
    newJob.save()
    try:
        newHistory = JobHistory.objects.create(job=newJob,
                                               jobStep=step,
                                               description="inicio",
                                               actual=1,
                                               status=2)

    except:
        newJob.delete()
        newlog = log.objects.create(process="Create Job",
                                    description="Error Save Job State")
        newlog.save()
        return JsonResponse({"status": False,
                             "message": "error ocurred when create job"})

    newHistory.save()
    return JsonResponse({"jobId": newJob.pk})


@api_view(['get'])
def getJob(request, pk):
    gJob = job.objects.filter(pk=pk)
    if not gJob.exists():
        return JsonResponse({"status": False,
                             "message": "error job dont exist"})
    gJob = gJob[0]
    stepHistory = JobHistory.objects.filter(job=pk)
    if not stepHistory.exists():
        return JsonResponse({"status": False,
                             "message": "error job dont exist"})
    steps = []
    for data in stepHistory:
        steps.append(data.Serialize())
    return JsonResponse(
            {"status": True,
             "jobid": gJob.pk,
             "step": steps
             },
            status=200)


@api_view(['PUT'])
def updateJob(request):
    _stepName = request.PUT['stepName']
    _jobId = request.PUT['jobId']
    _description = request.PUT['description']

    _step = JobStep.objects.get(name=_stepName)
    _job = job.objects.get(pk=_jobId)
    _stateJob = JobHistory.objects.get(job=_job, actual=1)
    _currentStep = _stateJob.jobStep.name
    _stateJob.end_time = datetime.now()
    _stateJob.actual = 0

    image_data = _job.image
    format, imgstr = image_data.split(';base64,')
    # ext = format.split('/')[-1]

    image = ContentFile(base64.b64decode(imgstr))
    # image = "'myphoto." + ext
    
    if _currentStep == "Invertir los colores":
        image = cv2.imread(image, 0)
        inverted_image = cv2.bitwise_not(image)
        cv2.imshow("Inverted Image", inverted_image)
        _stateJob.status = 1
    if _currentStep == "Pasar a Blanco y Negro":
    
        image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        image = cv2.threshold(image, 125, 255, cv2.THRESH_BINARY)[1]
        _stateJob.status = 1
    if _currentStep == "Rotal la imagen 90 grados":
        # Rotal la imagen 90 grados
        _stateJob.status = 1
    if _currentStep == "invertir la sobre el eje vertical":
        # invertir la sobre el eje vertical
        _stateJob.status = 1
    _stateJob.save()

    newHistory = JobHistory.objects.create(job=_job,
                                           jobStep=_step,
                                           description=_description,
                                           actual=1,
                                           status=2)

    return JsonResponse(
            {"status": True,
             "jobid": _job.pk,
             "step": newHistory.Serialize()
             },
            status=200)


@api_view(['get'])
def getLog(request):
    _inicio = request.GET['inicio']
    inicio = format_date(_inicio, 0)
    _final = request.GET['final']
    final = format_date(_final, 1)
    logs = log.objects.filter(date__range=(inicio, final))
    logsHistory = []

    for data in logs:
        logsHistory.append(data.Serialize())

    return JsonResponse({"logs": logsHistory})
