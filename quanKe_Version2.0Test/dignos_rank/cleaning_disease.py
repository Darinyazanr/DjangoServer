#encoding:utf-8
import json
import codecs
import MutalLevelCut
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#清理疾病本体数据
def clean_disease(indicfile):
    #print(json.dumps(indicfile, ensure_ascii=False, indent=6))
    indic=getSymptom_dic(indicfile)
    outdicfile = {}
    for k, v in indic.items():
        clean_arr=['src','html','symptom_symptom_probability','symptom_symptom_origin']
        for c in clean_arr:
            if c in k:
                v=''
        if not v.strip():
            continue
        elif 'exam_result' in k:
            vArr = v.split(' ')
            try:
                for i in vArr:
                    if ',' in i or '？' in i or '?' in i or '、' in i or '，' in i or '--' in i or '－－' in i or '；' in i:
                        i = i.replace('?', ',')
                        i = i.replace('——', ',')
                        i = i.replace('，', ',')
                        i = i.replace('；', ',')
                        tmp_arr = re.split(',|、|--|？|，', i)
                        s = delTailNumber(k)
                        for tmp in tmp_arr:
                            tmp_key = s + '_' + tmp
                            outdicfile[tmp_key] = 1
                    else:
                        s = delTailNumber(k)
                        tmp_key = s + '_' + i
                        outdicfile[tmp_key] =1
            except:
                pass
        elif 'symptom_symptom_example' in k:
            tmpArr = k.split('_')
            ss = getTailNumber(k)
            symptom_origin = '_'.join(tmpArr[:-1]) + '_origin' + ss
            if u'医学数据库' in indicfile[symptom_origin] or u'公众健康' in indicfile[symptom_origin]:
                outdicfile[k] = v
        elif 'examine' or 'exam_example' in k:
            exam_name=normalized_examName(v)
            outdicfile[k] = exam_name
        else:
            outdicfile[k] = v
    out_dic = normalized_symptomName(outdicfile)
    outDic=del_DiseaseNumber(out_dic)
    return outDic

#获取疾病本体的属性信息
def getSymptom_dic(dicInfo):
    disease_symptom={}
    for key in dicInfo.keys():
        if 'disease_clinical_manifestation' in key or 'disease_disease_definition' in key or 'disease_pathology' in key or 'disease_pathogenesis' in key:
            resDic = getSrcFeature(key, dicInfo[key], wantArr=['examine','lab','symptom','signs','frequency','youyi','adj','organ','position','reason','changes','exam_diag','treatment','prognosis'])
            for k, v in resDic.items():
                disease_symptom[k] = v
        elif 'src' in key:
            tmp = key.split('_')
            tmp_key = '_'.join(tmp[:-1])
            if 'symptom_src' in key:
                wantArr =['symptom','signs']
            elif 'sign_src' in key:
                wantArr =['symptom','signs']
            else:
                wantArr = ['examine', 'lab', 'symptom', 'signs', 'frequency', 'youyi', 'adj', 'organ', 'position', 'reason', 'changes', 'exam_diag', 'treatment', 'prognosis']
            resDic= getSrcFeature(tmp_key,dicInfo[key],wantArr)
            for k, v in resDic.items():
                disease_symptom[k] = v
        else:
            disease_symptom[key]=dicInfo[key]
    return disease_symptom

#分词获取本体特征
def getSrcFeature(key,src,wantArr=None):
    '''
    :param key:disease body key
    :param src: disease body src
    :param wantArr: wanna src
    :return: resDic key=list
    '''
    resDic={}
    app = MutalLevelCut.Cut_With_Regular()
    res = app.run(src)  # list
    #print json.dumps(res, ensure_ascii=False, indent=6)
    key = delTailNumber(key)
    for i in res:
        if isinstance(i, dict):
            tmp_key= key + '_' + i['signal']
            nmax = 0
            for res_key in resDic.keys():
                if resDic[res_key] == i['word']:
                    nmax=int(getTailNumber(res_key))-1
                    break
                if tmp_key in res_key:
                    num=getTailNumber(res_key)
                    nmax=max(nmax,num)
            new_num=int(nmax)+1
            last_key=tmp_key+str(new_num)
            for k, v in i.items():
                if k == 'signal' and v in wantArr:
                    resDic[last_key] = i['word']
    return resDic

# 去除key值后面的尾号
def delTailNumber(str):
    try:
        tmp = int(str[-1])
        str = str[:-1]
    except:
        pass
    try:
        tmp = int(str[-1])
        str = str[:-1]
    except:
        pass
    return str

#同义症状名称替换
def normalized_symptomName(indicfile):
    synonym_table='/home/dev/JeekerCode/disease_gbc_1209/data/symptomSynonym.txt'
    a = json.load(codecs.open(synonym_table, 'r', encoding='utf-8'))
    totalArr=[]
    for k, v in a.items():
        tmpArr = []
        tmpArr.append(k)
        spliArr = v.split('@')
        for i in spliArr:
            i=i.strip('\n')
            tmpArr.append(i)
        totalArr.append(tmpArr)
    for k,v in indicfile.items():
        if 'symptom' in k:
            for i in totalArr:
                if v in i:
                    indicfile[k]=i[0]
                    break
    return indicfile

#同义检查名称替换
def normalized_examName(exam_name):
    synonym_table='/home/dev/JeekerCode/disease_gbc_1209/data/examSynonym.txt'
    a = json.load(codecs.open(synonym_table, 'r',encoding='utf-8'))
    totalArr=[]
    for k, v in a.items():
        tmpArr = []
        k_arr=k.split('-->')
        #tmpArr.append(k_arr[0])
        tmpArr.append(k_arr[1])
        spliArr = v.split('@')
        for i in spliArr:
            i=i.strip('\n')
            tmpArr.append(i)
        totalArr.append(tmpArr)
    for i in totalArr:
        if exam_name in i:
            exam_name = i[0]
            break
    return exam_name


#取出key值最后的尾号
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

#字典中数据清除尾号
def del_DiseaseNumber(indic):
    outdic = {}
    for k, v in indic.items():
        out_k = delTailNumber(k)
        if type(v) in (int, float):
            s = out_k
            outdic[s] = v
        else:
            s = out_k+'_'+v
            outdic[s] = 1
    return outdic
