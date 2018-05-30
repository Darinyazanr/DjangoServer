import json
import codecs

def testConfig():
    rootPath=getPath()
    pathDic={}
    pathDic['model'] = rootPath+'/SGD_zhuyuan.pickle'
    pathDic['transformPk'] = rootPath+'/x_transform.pickle'
    pathDic['normalPk']=rootPath+'/MaxAbsScaler.pickle'
    #pathDic['featureName']=rootPath+'/FeatureNameArr.txt'
    #pathDic['disease_label'] = rootPath+'/Di_label.txt'
    pathDic['Y_label'] = rootPath+'/newY_label.txt'
    #pathDic['max_abs_scaler'] = '/home/dev/disease_modelv3.0/model/MaxAbsScaler.pickle'
    #pathDic['symptom_tongyi'] = rootPath+'/symptomSynonym.txt'
    #pathDic['exam_tongyi'] = rootPath+'/examSynonym.txt'
    #pathDic['disease_tongyi'] = rootPath+'/diseaseSynonym.txt'
    json.dump(pathDic,codecs.open('./CONFIG.txt','w',encoding='utf-8'),ensure_ascii=False)

def getPath(dataSource='data_1600'):
    import os
    s=os.getcwd()
    sArr=s.split('/')
    #print(sArr)
    reS='/'.join(sArr)+'/'+dataSource
    return reS

if __name__=='__main__':
    testConfig()    
    #getPath()
