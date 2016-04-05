from django.template import loader
from django.http import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse

from webclient.models import *
from datetime import datetime
from django.template import RequestContext

import os


from .models import Image

def index(request):
    latest_image_list = os.listdir('/home/jdas/Dropbox/Research/agriculture/agdss/image-store/')
    template = loader.get_template('webclient/index.html')

    context = {
        'latest_image_list': latest_image_list,
    }
    return HttpResponse(template.render(context, request))

@csrf_exempt
def applyLabels(request):
    dict = json.load(request)
    label_list_ = dict['label_list']
    image_name = dict['image_name']
    category_name = dict['category_name']
    sourceType = ''
    parentImage_ = Image.objects.all().filter(name = image_name);
    if not parentImage_:
        categoryTypeList = CategoryType.objects.all().filter(description=category_name);
        if(categoryTypeList):
            categoryType = categoryTypeList[0]
        else:
            categoryType = CategoryType(category_name=category_name,pub_date=datetime.now())
            categoryType.save()

        sourceTypeList = ImageSourceType.objects.all().filter(description="human");
        if (sourceTypeList):
            sourceType = sourceTypeList[0]
        else:
            sourceType = ImageSourceType(description="human",pub_date=datetime.now())
            sourceType.save()

        parentImage_ = Image(name=image_name, path = '/static/image-store/', description = "development test", source = sourceType, pub_date=datetime.now())
        parentImage_.save()
    else:
        labelObject = ImageLabels(parentImage = parentImage_[0], labelShapes=label_list_,pub_date=datetime.now())
        labelObject.save()
    return JsonResponse(label_list_,safe=False)


def loadLabels(request):
    parentImage_ = request.GET['image_name']
    label_list = []
    print parentImage_

    image = Image.objects.all().filter(name = parentImage_)
    if not image:
        print 'why here?'
        sourceType = ImageSourceType(description='machine',pub_date=datetime.now())
        sourceType.save()
        parentImage_ = Image(name=parentImage_, path='/static/image-store/',description='test generation at serverside', source=sourceType, pub_date=datetime.now())
        parentImage_.save()
    else:
        label_list = ImageLabels.objects.all().filter(parentImage=image[0],)

    responseText = ''
    if(label_list):
        responseText = responseText + label_list[0].labelShapes
    return JsonResponse(responseText, safe=False)


def purge(request):
    Image.objects.all().delete()
    ImageLabels.objects.all().delete()
    ImageSourceType.objects.all().delete()
    return HttpResponse("PURGED TABLES!")

