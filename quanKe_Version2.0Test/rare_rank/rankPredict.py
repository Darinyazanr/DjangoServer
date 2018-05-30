#encoding:utf-8
import numpy as np
import logging
import sys
import pickle
import scipy.sparse as sp
import json
import os
import codecs
import time

from .clean_bingli import clean_bingli_main




class PredictOnline(object):

    def __init__(self):
        self.configDic=json.load(codecs.open('./rareCONFIG.txt', 'r', encoding='utf-8'))
        self.Y = json.load(codecs.open(self.configDic['Y_label'], 'r', encoding='utf-8'))
        self.rareSymptom = self.configDic['rareSymptom']

        self.totalLibsvm=self.configDic['totalLibsvm']
	#clf=self.loadModel(self.configDic['model'])
	#self.feature_Arr =clf.feature_importances_
        self.rareDic=self.bingliDistance(self.totalLibsvm)

    def bingliDistance(self,totalSvm):
        from sklearn.datasets import load_svmlight_file
        X,y=load_svmlight_file(totalSvm)

        rareDic={}
        for index in range(0,X.shape[0]):
            li=rareDic.get(y[index],list([]))
            li.append(X[index])
            rareDic[y[index]]=li
        return rareDic

    def loadModel(self,dir):
        model=pickle.load(open(dir,'rb'))
        return model

    def disease_online(self,dic,transformPk):
        #dic={'main':{ },'disease1':{ },'disease2':{ }}
        resDic = {}  # {'disease1':0.5,'disease2':0.8}
	
        if 'main' in dic:
            main_dic=dic['main']
            #print('orgin:',main_dic)
            #main_data=self.process_main(main_dic)
            #print('process:',main_data)
            symptomArr=getSymptom(main_dic)            
            trainMain=transformPk.transform(main_dic)
            
            resDic=self.ensembleModels(symptomArr,trainMain,self.Y)
            returnDic={}
            returnDic['score']=resDic
            returnDic['feature']={}            
            #resDic=self.gbc_online(model,normalMain)
        return returnDic
    
    def ensembleModels(self,sympArr,newbingLi,Ylabel):
        '''
            :param sympArr:['发烧','头疼'] 类似这样的症状列表
            :param newbingLi: 已经被罕见病的Xtransform转码过的一条病例
            :return: 罕见疾病列表排名列表
        '''
        dic1=symptomDistance(sympArr,self.rareSymptom)
        #rareDic = bingliDistance()
        
        dic2=predictSimlar(newbingLi,rareDic=self.rareDic)

        #Y_label=json.load(open(YlabelFile,'r',encoding='utf-8'))
        dic3={}
        for k,v in dic2.items():
            dic3[Ylabel[k]]=v
        #print(dic1,dic3)


        #策略：将症状相似度和罕见疾病病例相似度  做权衡
        preDic={}
        for k,v in dic1.items():
            if v>=0.5:
                preDic[k]=v*0.5
        for k,v in dic3.items():
            if v>=1e-02:
                preDic[k]=preDic.get(k,0)+v/0.5
        print('-'*20)
        print(preDic)
        print('+'*20)
        return preDic
    #处理主函数
    def process_main(self,dic):
        dic=clean_bingli_main(dic)
        print('#'*10)
        #print dic
        #resTxt=self.read_main_dic(dic)
        return dic

def getSymptom(dic):#return Arr
    chief_sympArr=[]
    for k,v in dic.items():
        if 'chief_complaint_symptom_symptom_name' in k:
            temp=k.split('_')
            if len(temp)==6:
                chief_sympArr.append(temp[-1])
    print(chief_sympArr)
    return chief_sympArr

def symptomDistance(symptomArr,dicArrFile):
    dic=json.load(open(dicArrFile, 'r', encoding='utf-8'))
    dicScore={}
    for k,v in dic.items():

        temp=[0]*len(v)
        baseV=[1]*len(v)
        for index  in range(0,len(v)):
            for iindex in  range(0,len(symptomArr)):
                try:
                    if v[index]==symptomArr[iindex]:
                        temp[index]=1
                except:
                    pass
       #  print(temp)
       #  print(baseV)

        jishu=0
        for index in range(len(temp)):
            if temp[index]==baseV[index]:
               jishu+=1
        cos=float(jishu)/len(temp)
        dicScore[k]=cos
        #print(dicScore)
    return dicScore


def computeCosine(x,y):
    import numpy as np
    x = x.toarray().reshape(-1)
    y = y.toarray().reshape(-1)

    Lx = np.sqrt(x.dot(x))
    Ly = np.sqrt(y.dot(y))
    cos = x.dot(y) / (Lx * Ly)
    if np.isnan(cos):
        cos = -1
    return cos

def predictSimlar(newBingLi,rareDic):

    scoreDic={}
    for k,v in rareDic.items():
        if len(v)==1:
            print('1')
            score=computeCosine(newBingLi,v[0])
            scoreDic[int(k)]=score
        if len(v)==2:
            print('2')
            score=computeCosine(newBingLi,v[0])+computeCosine(newBingLi,v[1])
            scoreDic[int(k)]=score
        if len(v)>2:
            print('3')
            arr=[]
            for i in v:
                #s=spatial.distance.cosine(newBingLi,i)
                s=computeCosine(newBingLi,i)
                arr.append(s)
            #print(arr)
            arr=sorted(arr)
            score=sum(arr[1:-1])/float(len(arr[1:-1]))
            scoreDic[int(k)]=score
    #print(scoreDic)
    return scoreDic


if __name__=='__main__':
    pre=PredictOnline()

