#encoding:utf-8
from django.shortcuts import render

from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt

import json

import pickle
import codecs

from .rankPredict import *
from sklearn.feature_extraction import DictVectorizer

import time
import logging
import numpy as np

logging.getLogger().setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='./app_online.log',
                    filemode='a')





# Create your views here.
def index(request):

    return HttpResponse(

        "You should POST /cancer_predict/predict/ .")


# Disable CSRF, refer to https://docs.djangoproject.com/en/dev/ref/csrf/#edge-cases
#@csrf_exempt
predict_online=PredictOnline()

configDic=json.load(codecs.open('./rareCONFIG.txt', 'r', encoding='utf-8'))

transformPk=predict_online.loadModel(configDic['transformPk'])
#normalPk=predict_online.loadModel(configDic['normalPk'])

def dignos_predict(request):
    startTime=time.time()
    processWell=False
    if request.method == 'POST':
        body = json.loads(request.body)
        #print(json.dumps(body,ensure_ascii=False,indent=6))
        try:
            dic=predict_online.disease_online(body,transformPk)
            resDic = json.dumps(dic, ensure_ascii=False)
            processWell=True
        except Exception as e:
            processWell=False
            resDic=e
            raise Exception(e)
        finally:
            now=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            serverIP='192.168.8.41'
            softWareVersion='Version0.1'
            clientName='NoClientName'
            clientIp=request.META['REMOTE_ADDR']
            requestBody=body
            requestClass="model_disease"
            responseBody=resDic

            #responseBody=resDic
            endTime=time.time()
            takeTime=endTime-startTime #*1000  s->ms
            logging.info('nowTime:[{}] serverIP:[{}] softWareVersion:[{}] userName:[{}] userIP:[{}] requestType:[{}] requestBody:[{}] success:[{}] responseBody:[{}] takeTime:[{}]'.format(now,serverIP,softWareVersion,clientName,clientIp,requestClass,requestBody,processWell,responseBody,takeTime*1000))
        return HttpResponse(resDic)
    else:
        if request.method=='GET':
            return HttpResponse("Only support Post request")
