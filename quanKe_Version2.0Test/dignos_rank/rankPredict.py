#encoding:utf-8
import numpy as np
import logging
import sys
import pickle
import scipy.sparse as sp
import json
import os
import codecs
from sklearn import preprocessing
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier

#reload(sys)
#sys.setdefaultencoding('utf-8')
from .clean_bingli import clean_bingli_main




class PredictOnline(object):

    def __init__(self):
        self.configDic=json.load(codecs.open('./CONFIG.txt', 'r', encoding='utf-8'))
        self.Y = json.load(codecs.open(self.configDic['Y_label'], 'r', encoding='utf-8'))
        #self.disease_label = json.load(codecs.open(self.configDic['disease_label'], 'r', encoding='utf-8'))
        #self.disease_Feature=json.load(codecs.open(self.configDic['featureName'], 'r', encoding='utf-8'))
	#clf=self.loadModel(self.configDic['model'])
	#self.feature_Arr =clf.feature_importances_

    def loadModel(self,dir):
        model=pickle.load(open(dir,'rb'))
        return model

    def disease_online(self,dic,model,transformPk,normalPk):
        #dic={'main':{ },'disease1':{ },'disease2':{ }}
        resDic = {}  # {'disease1':0.5,'disease2':0.8}
	
        if 'main' in dic:
            main_dic=dic['main']
            #print('orgin:',main_dic)
            #main_data=self.process_main(main_dic)
            #print('process:',main_data)
            transMain=transformPk.transform(main_dic)
            normalMain=normalPk.transform(transMain)
            #print(normalMain)
            resDic=self.gbc_online(model,normalMain)
        return resDic
            

    def gbc_online(self,model, X_test):
        clf = model
        start = time.time()
        '''
	print '+'*10
	#feature_Arr =clf.feature_importances_
        x_testIndex=np.nonzero(X_test)#tuple(array([]),array([]))
        x_testIndex=x_testIndex[1]
	self.feature_Arr =clf.feature_importances_
        FeatureScoreArr=[]
        for index in x_testIndex:
            FeatureScoreArr.append(self.feature_Arr[index])        
	FeatureScoreArr=np.array(FeatureScoreArr)
        featureMax_Arr = np.argsort(-FeatureScoreArr)
        #FeatureName = self.disease_Feature
 	reallyIndex=[]
        for index in featureMax_Arr.tolist():
            reallyIndex.append(x_testIndex[index])
	
	resFeatureDic={}
	resFeatureArr=[]
        for index in reallyIndex:
            resFeatureArr.append(self.disease_Feature[index])
	resFeatureDic['feature']=resFeatureArr[:50]#just get top_50
        print json.dumps(resFeatureDic,ensure_ascii=False,indent=6)	
	print '+'*10
        '''
        #answer = clf.predict(X_test)
        proba = clf.predict_proba(X_test)
        classes=model.classes_
        classes=list(classes)
        #print('classes:',classes)
        nMax = np.argsort(-proba)
        # big->small
        sortProba = np.array([proba[line_id, i] for line_id, i in enumerate(np.argsort(-proba, axis=1))])

        #Y = json.load(codecs.open(self.configDic['Y_label'], 'r', encoding='utf-8'))
        print('$' * 10)
        Nindex = nMax[0]
        Npro = sortProba[0]
        #print ('---->' + Y[answer[0]])
        NNindex=[]
        for ii in Nindex[:10]:
            NNindex.append(classes[ii])
        resDic={}
        for ii in range(10):
            resDic[self.Y[int(NNindex[ii])]]=Npro[ii]
        print(json.dumps(resDic,ensure_ascii=False,indent=6))
        print('$' * 10)
        end = time.time()
        print('Take Time:', end - start)
        resDic_addft={}
        resDic_addft['feature']={}
        resDic_addft['score']=resDic
        return  resDic_addft  
    '''
    def getExamNameAndDiag(self,dic):
        examDic={}
	for k,v in dic.items():
	    if 'patient_jianchabaogao_content_exam_report_exam_item_name' in k:
		examDic[k]=v
	    if 'patient_jianchabaogao_content_exam_report_exam_diag_src' in k:
		examDic[k]=v
	return examDic

    def getExamRank(self,examDic,diseaseDic,diseaseName):
	rankDic={}
	diseaseExamDic={}
	for k,v in diseaseDic.items():
	    try:
	        if 'disease_diagnosis_diagnosis_condition_exam_exam_example' in k:
		    diseaseExamDic[k]=v
		if 'disease_diagnosis_diagnosis_condition_exam_exam_result' in k:
		    diseaseExamDic[k]=v
	    except:
		pass
	for k,v in diseaseExamDic.items():
	    if 'disease_diagnosis_diagnosis_condition_exam_exam_example' in k:
		num=getTailNumber(k)
		tmpArr=k.split('_')
		tmpS='_'.join(tmpArr[:-1])+'_result'+num
		try:
		    tmpV=diseaseExamDic[tmpS]
		except:
		    tmpV=''
		for kk,vv in examDic.items():
		    if v in vv:
			num1=getTailNumber(kk)
                	tmpArr1=kk.split('_')
                	tmpS1='_'.join(tmpArr1[:-2])+'_diag_src'+num1
			try:
	                    tmpV1=examDic[tmpS1]
        	        except:
                	    tmpV1=''
			#diag_src  && exam_sult
			if tmpV !='' and tmpV1 !='' and tmpV in tmpV1:
			    rankDic[diseaseName]=rankDic.get(diseaseName,0)+1
	return rankDic 
	
    #根据疾病名字获取疾病特征  暂时没用
    def get_diseaseFeature(self,disease_name):
        folder_path='/home/dev/disease_modelv4.0/data/features/disease_feature'
        file_list = os.listdir(folder_path)
        print(file_list)
        disease_symptom = {}
        for file_index, file_name in enumerate(file_list):
            print(file_name)
            (shotname, extension) = os.path.splitext(file_name)
            #print(shotname)
            #print(disease_name)
            if disease_name==shotname:
                file_path = os.path.join(folder_path, shotname + extension)
                f = codecs.open(file_path, 'r', encoding='utf-8')
                dicInfo = json.load(f)
                for key in dicInfo.keys():
                    disease_symptom[key] = dicInfo[key]
            return disease_symptom
    '''
    #处理主函数
    def process_main(self,dic):
        dic=clean_bingli_main(dic)
        print('#'*10)
        #print dic
        #resTxt=self.read_main_dic(dic)
        return dic
    '''
    def process_disease(self, dic):
        resTxt = self.read_disease_dic(dic)
        return resTxt
    
    #映射病例main{}中索引
    def read_main_dic(self,X_train):
        X_main = []
        for k, v in X_train.items():
            try:
                X_main.append(str(k)+ ':' + str(v))
                #print(json.dumps(k+':'+str(v),ensure_ascii=False,indent=6))
            except:
                print(json.dumps(k+':'+str(v),ensure_ascii=False,indent=6))
        return X_main
    
    #映射疾病disease{}中的索引
    def read_disease_dic(self, X_item):
        X_disease=[]
        for k, v in X_item.items():
            try:
                X_disease.append(str(self.features[k]) + ':' + str(v))
            except:
                print(json.dumps(k+':'+str(v),ensure_ascii=False,indent=6))
        return X_disease

    #特征排序
    def sortX(self,X):
        X=set(X)
        resArr=[]
        dic={}
        for i in X:
            arr=i.split(':')
            dic[arr[0]]=arr[1]
        X=sorted(dic.items(),key=lambda asd:int(asd[0]))
        for i in X:
            tmp=i[0]+':'+i[1]
            resArr.append(tmp)
        return resArr

def getTailNumber(s):
    try:
        tmp = int(s[-1])
        s = s[:-1]
        tmp=str(tmp)
    except:
        pass
    try:
        tmp1 = int(s[-1])
        s = s[:-1]
        tmp=str(tmp1)+tmp
    except:
        pass
    return tmp
    '''
if __name__=='__main__':
    pre=PredictOnline()

