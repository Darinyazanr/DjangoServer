#encoding:utf-8
import codecs
import json
import re

#共同路径
PATH='/home/jq/medical_modelv1.0/'

#病例数据清洗主函数，输入参数为病例dic
def clean_bingli_main(indicfile):
    outdicfile = {}
    info_age = 'age_value'
    sex_name = 'sex_name'
    marital_status_name='marital_status_name'
    zhusu = 'chief_complaint'
    xianbingshi = 'history_of_present_illness'
    jiwangshi = 'history_of_past_illness'
    gerenshi = 'social_history'
    tigejiancha='physical_examination'
    jianchabaogao='jianchabaogao'
    jianyanbaogao='jianyanbaogao'

    for k, v in indicfile.items():
        if info_age in k:
            outdicfile[k] = float(v)/100
        elif sex_name in k:
            if v == u'男':
                outdicfile[k] = 1
            else:
                outdicfile[k] = 0
        elif marital_status_name in k:
             if v == u'已婚':
                outdicfile[k] = 1
             else:
                outdicfile[k] = 0
        #清理主诉
        elif zhusu in k:
            for key, value in v.items():
                a = clean_zhusu(key, value)
                if a != None:
                    if key == 'symptom':
                        zhusu_key=zhusu + '_' + key
                        outdic=symptom_model(zhusu_key,value)
                        outdicfile=dict(outdicfile,**outdic)
                    elif key == 'disease':
                        #取出每个疾病
                        for li in a:
                            for key2, value2 in li.items():
                                try:
                                    disease_name=li['disease_name']
                                    normalized_disease_name=normalized_diseaseName(disease_name)
                                    disease_key = zhusu + '_' + key + '_' + 'disease_name'+'_'+normalized_disease_name
                                    outdicfile[disease_key] = 1
                                    if key2=='symptom':
                                        zhusu_key=disease_key+'_'+key2
                                        outdic = symptom_model(zhusu_key, value2)
                                        outdicfile = dict(outdicfile, **outdic)
                                    elif key2=='classification':
                                        out_key = disease_key + '_' + key2+'_'+value2
                                        outdicfile[out_key] = 1
                                except:
                                    pass
                    elif key == 'sign':
                        for li in a:
                            for key2, value2 in li.items():
                                if key2 == 'sign_name':
                                    out_key = zhusu + '_' + key + '_' + key2+'_'+value2
                                    outdicfile[out_key] = 1
                    elif key=='return_visit':
                        for key2, value2 in value.items():
                            if key2 == 'return_visit_indicator':
                                out_key = zhusu + '_' + key + '_' + key2
                                try:
                                    outdicfile[out_key] = float(value2)
                                except:
                                    if value2==u'是':
                                        outdicfile[out_key] =1
                                    elif value2==u'否':
                                        outdicfile[out_key] = 0
                                    elif value2=='True':
                                        outdicfile[out_key] = 1
                                    elif value2=='False':
                                        outdicfile[out_key] = 0
                                    else:
                                        out_key=out_key+'_'+value2
                                        outdicfile[out_key] = 1
                            elif key2=='disease':
                                out_key =zhusu + '_' + key + '_' + key2 + '_' + value2
                                outdicfile[out_key] = 1
        #清理现病史
        elif xianbingshi in k:
            times = v['time']
            #每一个时间节点
            for time in times:
                for key, value in time.items():
                    a = clean_xianbingshi(key, value)
                    if a != None:
                        if key == 'symptom':
                            xianbingshi_key= xianbingshi+ '_' + key
                            outdic=symptom_model(xianbingshi_key,value)
                            outdicfile = dict(outdicfile, **outdic)
                        elif key == 'sign':
                            #每一个体征
                            for li in a:
                                for key2, value2 in li.items():
                                    if (isinstance(value2,str) and u'体温' in value2) or (isinstance(value2,str) and '℃' in value2) or (isinstance(value2,str) and u'度' in value2):
                                        result=range_normalized('temperature',value2)
                                        if result!=u'正常':
                                            out_key = xianbingshi + '_' + key + '_' + key2 + '_' + result
                                            outdicfile[out_key] = 1
                                    elif key2 == 'sign_name':
                                        tmp_arr=value2.split(' ')
                                        for tmp in tmp_arr:
                                            out_key = xianbingshi + '_' + key + '_' + key2+'_'+tmp
                                            outdicfile[out_key] = 1
                        elif key == 'negative_state_description':
                            out_key = xianbingshi + '_' + key+'_'+value
                            outdicfile[out_key] = 1
                        elif key == 'diagnose':
                            for key2, value2 in value.items():
                                if key2 == 'diagnosis_name':
                                   try:
                                        tmp_arr = re.split(' |、|,|，', value2)
                                        for tmp in tmp_arr:
                                            normalized_disease_name=normalized_diseaseName(tmp)
                                            if normalized_disease_name!=None:
                                                out_key = xianbingshi+ '_' + key + '_' + key2+'_'+normalized_disease_name
                                                outdicfile[out_key] = 1
                                   except:
                                       pass
        #清理既往史
        elif jiwangshi in k:
            for key, value in v.items():
                a = clean_jiwangshi(key, value)
                if a != None:
                    if key=='symptom':
                        jiwangshi_key = jiwangshi + '_' + key
                        outdic = symptom_model(jiwangshi_key, value)
                        outdicfile = dict(outdicfile, **outdic)
                    elif key=='disease':
                        #li为每个疾病模型
                        for li in a:
                            for key2, value2 in li.items():
                                try:
                                    #取出疾病名字
                                    disease_name = normalized_diseaseName(li['disease_name'])
                                    if disease_name!=None:
                                        disease_key = jiwangshi + '_'+key+'_disease_name'+'_'+disease_name
                                        outdicfile[disease_key] = 1
                                        if 'duration_of_illness' in key2 and 'unit' not in key2:#时间归一化以'天'为单位
                                            tmp_key=key2+'_'+'unit'
                                            if type(value2) == int or type(value2) == float:
                                                normalized_duration = time_normalized(value2, li[tmp_key])
                                                out_key =disease_key+ '_' + key2
                                                outdicfile[out_key] = normalized_duration
                                            elif type(value2) == str:
                                                try:
                                                    tmpArr = value2.split('-')
                                                    low = float(tmpArr[0])
                                                    high = float(tmpArr[1])
                                                    v = (low + high) / 2
                                                    normalized_duration = time_normalized(value2, li[tmp_key])
                                                    out_key =disease_key+ '_' + key2
                                                    outdicfile[out_key] = normalized_duration
                                                except:
                                                    pass
                                        elif 'duration_of_illness_unit' in key2:
                                            pass
                                        elif key2=='classification':
                                            out_key =disease_key+'_'+key2+'_'+value2
                                            outdicfile[out_key] = 1
                                        elif key2 == 'symptom':
                                            jiwangshi_key=disease_key+'_'+key2
                                            outdic=symptom_model(jiwangshi_key,value2)
                                            outdicfile = dict(outdicfile, **outdic)
                                except:
                                    pass
        #清理个人史
        elif gerenshi in k:
            for key, value in v.items():
                a = clean_gerenshi(key, value)
                if a != None:
                    out_key = gerenshi + '_' + key
                    try:
                        outdicfile[out_key] = float(a)
                    except:
                        if a==u'是':
                            outdicfile[out_key] =1
                        elif a==u'否':
                            outdicfile[out_key] = 0
                        elif a=='True':
                            outdicfile[out_key] = 1
                        elif a=='False':
                            outdicfile[out_key] = 0
                        else:
                            out_key=out_key+'_'+a
                            outdicfile[out_key] = 1
        #清理体格检查
        elif tigejiancha in k:
            for key, value in v.items():
                a = clean_tigejiancha(key, value)
                if a != None:
                    value_arr = [u'有力', u'齐', u'正常', u'无', u'良好',u'清楚',u'自如',u'未',u'灵敏',u'双',u'各',u'呼吸规整',u'平坦',u'次/分',u'软',u'充盈',u'红润',u'否',u'是',u'不大','自由活动',u'见专科检查',u'对称','A2、p2','光滑']
                    if isinstance(a, list):
                        for li in a:
                            for key2,value2 in li.items():
                                count=0
                                for s in value_arr:
                                    if s in value2:
                                        count=count+1
                                if count==0:
                                    key_arr = ['src','size']
                                    if key2 in key_arr:
                                        pass
                                    else:
                                        out_key=tigejiancha+'_'+key+'_'+key2
                                        try:
                                            outdicfile[out_key] = float(value2)
                                        except:
                                            if value2 == u'是':
                                                outdicfile[out_key] = 1
                                            elif value2 == u'否':
                                                outdicfile[out_key] = 0
                                            elif value2 == 'True':
                                                outdicfile[out_key] = 1
                                            elif value2 == 'False':
                                                outdicfile[out_key] = 0
                                            else:
                                                out_key = out_key + '_' + value2
                                                outdicfile[out_key] = 1
                    else:
                        count = 0
                        for s in value_arr:
                            if s in a:
                                count = count + 1
                        if count ==0:
                            arr = ['temperature', 'blood_pressure', 'heart_rate','pulse','breath','systolic_pressure','diastolic_pressure']
                            if key in arr:
                                result=range_normalized(key,a)
                                if result != u'正常' and result!='':
                                    out_key = tigejiancha + '_' + key+'_'+result
                                    outdicfile[out_key]=1
                            elif key=='abdomen_limp__shape':
                                if '一' in a:
                                    tmp_arr=a.split('一')
                                    for tmp in tmp_arr:
                                        if tmp!='':
                                            out_key = tigejiancha + '_' + key+'_'+tmp
                                            outdicfile[out_key]=1
                                else:
                                    out_key = tigejiancha + '_' + key+'_'+a
                                    outdicfile[out_key]=1
                            elif key=='yellow_part':
                                tmp_arr=a.split('、')
                                for tmp in tmp_arr:
                                    out_key = tigejiancha + '_'+ key+'_'+tmp
                                    outdicfile[out_key]=1
                            elif key=='physiological_reflex':
                                if u'存在' in a and '，' in a:
                                    pass
                                else:
                                    out_key = tigejiancha + '_'+ key+'_'+a
                                    outdicfile[out_key]=1
                            else:
                                out_key = tigejiancha + '_' + key
                                try:
                                    outdicfile[out_key] = float(a)
                                except:
                                    if a == u'是':
                                        outdicfile[out_key] = 1
                                    elif a == u'否':
                                        outdicfile[out_key] = 0
                                    elif a == 'True':
                                        outdicfile[out_key] = 1
                                    elif a == 'False':
                                        outdicfile[out_key] = 0
                                    else:
                                        out_key = out_key + '_' + a
                                        outdicfile[out_key] = 1
        #清理检查报告
        elif jianchabaogao in k:
            #取出检查列表中的每一个检查
            for li in v:
                for key,value in li.items():
                    a=clean_jianchabaogao(key,value)
                    if a!=None:
                        try:
                            exam_class_name=li['exam_class_name']
                            exam_item_name=li['exam_item_name']
                            exam_key=jianchabaogao+'_'+exam_class_name+'_'+'exam_item_name'+'_'+exam_item_name
                            if key=='exam_diag_quantization':
                                #每一个检查结论
                                for li in a:
                                    quantization_project = li['quantization_project']
                                    for key2,value2 in li.items():
                                        if key2=='quantization_num':
                                            quantization_num_min=li['quantization_num_min']
                                            quantization_num_max=li['quantization_num_max']
                                            if value2<quantization_num_min:
                                                out_key=exam_key+'_'+'quantization_project'+'_'+quantization_project+'_'+'quantization_num'+'_'+'偏低'
                                                outdicfile[out_key] =1
                                            elif value2>quantization_num_max:
                                                out_key = exam_key + '_' +'quantization_project'+'_'+quantization_project+'_'+'quantization_num'+'_'+'偏高'
                                                outdicfile[out_key] = 1
                                        elif key2=='quantization_text' and value2!='正常':
                                            out_key = exam_key + '_' + 'quantization_project' + '_' + quantization_project + '_' + 'quantization_text'
                                            tmp_arr = re.split('、|,|，| |_|.|:', value2)
                                            for tmp in tmp_arr:
                                                arr=[u'未见明显异常','3','4','5','6','7','1','',u'考虑',u'考虑为',u'心肌断层显像']
                                                if tmp in arr:
                                                    pass
                                                else:
                                                    try:
                                                        outdicfile[out_key] = float(tmp)
                                                    except:
                                                        if tmp== u'是':
                                                            outdicfile[out_key] = 1
                                                        elif tmp == u'否':
                                                            outdicfile[out_key] = 0
                                                        elif tmp== 'True':
                                                            outdicfile[out_key] = 1
                                                        elif tmp== 'False':
                                                            outdicfile[out_key] = 0
                                                        else:
                                                            out_key = out_key + '_' + tmp
                                                            outdicfile[out_key] = 1
                                        elif key2=='quantization_boolean':
                                            out_key = exam_key + '_'+'quantization_project'+'_'+quantization_project+'_'+'quantization_boolean'
                                            try:
                                                outdicfile[out_key] = float(value2)
                                            except:
                                                if value2 == u'是':
                                                    outdicfile[out_key] = 1
                                                elif value2 == u'否':
                                                    outdicfile[out_key] = 0
                                                elif value2 == 'True':
                                                    outdicfile[out_key] = 1
                                                elif value2 == 'False':
                                                    outdicfile[out_key] = 0
                                                else:
                                                    out_key = out_key + '_' + value2
                                                    outdicfile[out_key] = 1
                                        elif key2=='quantization_sub':
                                            #取出每一个量化项目细化
                                            for li in value2:
                                                for key3,value3 in li.items():
                                                    quantization_project=li['quantization_project']
                                                    if key3=='quantization_text' and value3!='正常':
                                                        out_key = exam_key + '_' + key2+'_'+'quantization_project'+'_'+quantization_project+'_'+key3
                                                        tmp_arr = re.split('、|,|，| |_|.|:', value3)
                                                        for tmp in tmp_arr:
                                                            arr = [u'未见明显异常', '3', '4', '5', '6', '7', '1', '',u'考虑',u'考虑为',u'心肌断层显像']
                                                            if tmp in arr:
                                                                pass
                                                            else:
                                                                try:
                                                                    outdicfile[out_key] = float(tmp)
                                                                except:
                                                                    if tmp== u'是':
                                                                        outdicfile[out_key] = 1
                                                                    elif tmp == u'否':
                                                                        outdicfile[out_key] = 0
                                                                    elif tmp== 'True':
                                                                        outdicfile[out_key] = 1
                                                                    elif tmp== 'False':
                                                                        outdicfile[out_key] = 0
                                                                    else:
                                                                        out_key = out_key + '_' + tmp
                                                                        outdicfile[out_key] = 1
                        except:
                            pass
        #清理检验报告
        elif jianyanbaogao in k:
            #取出检验列表中的每一个检验
            for li in v:
                try:
                    lab_sub_item_name=li['lab_sub_item_name']
                    lab_result_value=li['lab_result_value']
                    lab_qual_result=li['lab_qual_result']
                    result_status_code=li['result_status_code']
                    range=li['range']
                    tmp_key = jianyanbaogao + '_' +lab_sub_item_name
                    if lab_qual_result!='':
                        arr=['阴性','阳性','+-','+','-','1+','2+','3+']
                        for a in arr:
                            if a in lab_qual_result:
                                out_key = tmp_key + '_' + 'lab_qual_result' +'_'+a
                                outdicfile[out_key] = 1
                    if result_status_code=='H':
                        out_key = tmp_key + '_' + 'lab_result_value' + '_'+u'偏高'
                        outdicfile[out_key] = 1
                    elif result_status_code == 'L':
                        out_key = tmp_key + '_' + 'lab_result_value' +'_'+ u'偏低'
                        outdicfile[out_key] = 1
                    elif result_status_code ==None:
                        if lab_result_value!='' and range!='':
                            if '<' in range:
                                range_value = re.sub('\D', '', range)
                                if float(lab_result_value) >= float(range_value):
                                    out_key = tmp_key + '_' + 'lab_result_value' +'_'+ u'偏高'
                                    outdicfile[out_key] = 1
                            elif '≤' in range:
                                range_value = re.sub('\D', '', range)
                                if float(lab_result_value) > float(range_value):
                                    out_key = tmp_key + '_' + 'lab_result_value' +'_'+ u'偏高'
                                    outdicfile[out_key] = 1
                            elif '-' in range or '--' in range or '---' in range:
                                range_arr = re.split('-|--|---', range)
                                if float(lab_result_value)<float(range_arr[0]):
                                    out_key=tmp_key+'_'+'lab_result_value'+'_'+u'偏低'
                                    outdicfile[out_key]=1
                                elif float(lab_result_value)>float(range_arr[1]):
                                    out_key = tmp_key + '_' + 'lab_result_value' +'_'+ u'偏高'
                                    outdicfile[out_key] = 1
                except:
                        pass
    return outdicfile

#主诉数据清洗 #无伴随症状为文本特征
def clean_zhusu(k, v):
    str = ['symptom', 'sign', 'disease','return_visit']
    if k in str:
        return v

# 现病史清洗 #检查结论为文本特征
def clean_xianbingshi(k, v):
    str = ['symptom', 'sign', 'negative_state_description', 'diagnose']
    if k in str:
        return v

# 既往史清洗
def clean_jiwangshi(k, v):
    str = ['disease','symptom']
    if k in str:
        return v

# 个人史数据清洗
def clean_gerenshi(k, v):
    str = ['smoke_indicator', 'drink_indicator']
    for s in str:
        if s in k:
            return v
"""
# 体格检查清洗
def clean_tigejiancha(k, v):
    #心尖搏动位置，心尖搏动描述,左上肢血压,右上肢血压,头围,胸围,身高,身高单位,体重,体重单位,孕前身高,孕前身高单位,,孕前体重,孕前体重单位,体表面积,BMI,评分,血氧饱和度,发育,营养,体型,入室类型,
    #神志,精神,反应,哭声,四肢动作,姿势,体位,步态,面容类型,面色,口角歪斜,鼻唇沟变浅,表情,查体是否合作,皮肤温度,皮肤湿度,皮肤弹性,毛发分布是否正常
    #足跖纹理,指趾甲情况,头颅前囟,前囟张力,头颅后囟,眉毛,睫毛,龋齿,缺牙,义齿,牙残根,斑釉牙,牙齿松动,齿列整齐,咽后壁,咽腔,咽侧索,咽腭垂,喉发音清晰,声音是否正常,喉嘶哑
    #颈部对称性,颈项粗短,颈部软硬,脐残端脱落情况,脐残端分泌物,脐残端脐轮,包皮,阴囊,睾丸,睾丸降入阴囊,附睾,精索,鞘膜积液,男性发育畸形,女性阴毛.大阴唇,小阴唇,阴蒂,阴阜,阴道
    #子宫,输卵管,卵巢,四肢毛细血管再充盈时间,四肢毛细血管再充盈时间单位,下肢周径右大腿,下肢周径右小腿,下肢周径左大腿,下肢周径左小腿,四肢低皮温侧别对比,肌力,A2,P2,腹部胃肠蠕动波，哮鸣音,病理反射(概述),肌张力,肌力
    str=['apex_beat_position','apex_beat_description','src','left_blood_pressure','right_blood_pressure','head_circumference','chest_circumference','height','height_unit','weight'
        ,'weight_unit','height_before_pregnancy','height_before_pregnancy_unit','weight_before_pregnancy','weight_before_pregnancy_unit','surface_area'
         ,'bmi','score','spo2','development','nutrition','shape','into_room_tyoe','mind','spirit','reaction','cry','limbs_movement','posture','position','gait'
        ,'face_type','face_color','distortion_of_commissure','nasolabial_groove_shallowing','expression','cooperative','skin_temperature','skin_humidity','skin_elastic','hair_distribution','toe_texture','toe_nails'
        ,'head_bregmatic_fontanel','anterior_fontanel_tension','head_posterior_fontanel','eyebrow','eyelash',
        'dental_caries','missing_teeth','false_teeth','residual_root','mottled_teeth','loose_teeth','neat_teeth','pharyngeal_retropharynx','cavum_pharyngis','lateral_pharyngeal_bands','pharyngeal_uvula_position'
        ,'throat_pronunciation_clear','throat_abnormal','throat_hoarse','neck_symmetry','neck_tubbiness','neck_soft_hard','umbilical_stump_abscission','umbilical_stump_secretion','umbilical_stump_navel_around'
        ,'prepuce','scrotum','testis','testis_into_scrotum','epididymis','spermatic_cord','hydrocele','male_deformity','female_pubic_hair','labium_majus','labia_minora','clitoris','mons_pubis','vagina','uterus'
        ,'fallopian_tube','ovary','arms_and_legs_capillary_refill_time','arms_and_legs_capillary_refill_time_unit','lower_limbs_circumference_right_thigh','lower_limbs_circumference_right_crus','lower_limbs_circumference_left_thigh'
        ,'lower_limbs_circumference_left_crus','arms_and_legs_skin_temperature_lower','muscle_strengt','a_2_and_p_2','abdomen_gastrointestinal_peristaltic_wave','wheezing_rale','muscle_strength','pathologic_reflex','muscle_tension','muscle_strength'
         ]
    if k not in str:
        return v
"""
#体格检查
def clean_tigejiancha(k,v):
    str=['temperature','pulse','breath','blood_pressure','systolic_pressure','diastolic_pressure']
    if k in str:
        return v

#检查报告清洗
def clean_jianchabaogao(k,v):
    str=['exam_class_name','exam_item_name','exam_diag_quantization']
    if k in str:
        return v

# 检查报告清洗
def clean_jianyanbaogao(k, v):
    str = ['lab_sub_item_name', 'lab_result_value', 'lab_qual_result','range']
    if k in str:
        return v

#symptom模块处理,v为symptom模型结构
def symptom_model(key,value):
    outdic={}
    #symptom为症状列表，li为单个症状字典
    for li in value:
        for k, v in li.items():
            try:
                #去掉了无伴随症状和无关诱因
                tmp_arr = ['symptom_range_description','freq','freq_change','freq_change_describe','symptom_name','no_induce','occurrence_time_of_symptom','duration_indicator','no_accompany_symptoms','menstruation','menstrual_cycle','menstrual_cycle_unit','menstrual_days','menstrual_days_unit','last_menstrual_period','expected date of delivery','early_pregnancy_test_positive_time','early_pregnancy_reaction_time','fetal_movement_time']
                symptom_name = normalized_symptomName(li['symptom_name'])
                symptom_key =key+'_' + 'symptom_name' + '_' + symptom_name
                outdic[symptom_key] = 1
                del_arr=['同前','如前','相似','上述症状']
                if v in del_arr:
                    pass
                elif k== 'property':#症状性质
                    try:
                        tmp_arr = re.split(' |、|,|，', v)
                        for tmp in tmp_arr:
                            out_key = symptom_key + '_' + k + '_' + tmp
                            outdic[out_key] = 1
                    except:
                        out_key = symptom_key + '_' + k+ '_' + v
                        outdic[out_key] = 1
                elif k== 'induce' or k=='aggravation_factors':#症状诱因,频率,导致加重的因素
                    tmp_arr = v.split(' ')
                    for tmp in tmp_arr:
                        out_key = symptom_key + '_' + k+ '_' + tmp
                        outdic[out_key] = 1
                elif k=='medicine_recovery':
                    for k2,v2 in v.items():
                        if k2=='medicine_name':
                            out_key = symptom_key + '_' + k+'_'+k2
                            outdic[out_key] = v2
                elif 'duration_of' in k and 'unit' not in k:#时间归一化以'天'为单位
                    tmp_key=k+'_'+'unit'
                    if type(v) == int or type(v) == float:
                        normalized_duration = time_normalized(v, li[tmp_key])
                        out_key = symptom_key + '_' + k
                        outdic[out_key] = normalized_duration
                    elif type(v) == str:
                        try:
                            tmpArr = v.split('-')
                            low = float(tmpArr[0])
                            high = float(tmpArr[1])
                            v = (low + high) / 2
                            normalized_duration = time_normalized(v, li[tmp_key])
                            out_key = symptom_key + '_' + k
                            outdic[out_key] = normalized_duration
                        except:
                            pass
                elif 'unit' in k:
                    pass
                elif k not in tmp_arr:
                    if isinstance(v, list):
                        #每个伴随或不伴随症状
                        for accompany in v:
                            for k2, v2 in accompany.items():
                                if k2 == 'symptom_name':
                                    normalized_symptom= normalized_symptomName(v2)
                                    out_key = symptom_key + '_' + k + '_' + normalized_symptom
                                    outdic[out_key] = 1
                    else:
                        out_key = symptom_key + '_' + k
                        try:
                            outdic[out_key] = float(v)
                        except:
                            if v==u'是':
                                outdic[out_key] = 1
                            elif v==u'否':
                                outdic[out_key] = 0
                            elif v=='True':
                                outdic[out_key] = 1
                            elif v=='False':
                                outdic[out_key] = 0
                            else:
                                out_key = out_key + '_' + v
                                outdic[out_key] = 1
            except:
                pass
    return outdic

#时间单位归一化
def time_normalized(time_value, time_unit):
    try: 
        time_value=float(time_value)
        if time_unit=='年':
            return time_value * 365
        elif time_unit=='月':
            return time_value * 30
        elif time_unit=='周':
            return time_value * 7
        elif time_unit=='天':
            return time_value
        elif time_unit=='小时':
            return time_value / 24
        elif time_unit=='分钟':
            return 0.1
        elif time_unit=='秒':
            return 0.05
    except Exception as e:
        print('error', e)
        print(time_unit)

#体温、血压、心率、舒张压、收缩压等根据标准范围归一化
def range_normalized(key,value):
    result=''
    #体温
    if key=='temperature':
        tmpArr = value.split(' ')
        max_value = 0
        tmp_max_value = 0
        try:
            for tmp in tmpArr:
                if '-' in tmp:
                    tmp_arr = tmp.split('-')
                    for tmp1 in tmp_arr:
                        value = filter(lambda x: x in '0123456789.', tmp1)
                        tmp_max_value = max(float(value), tmp_max_value)
                        max_value = max(max_value, tmp_max_value)
                elif tmp!='':
                    value = filter(lambda x: x in '0123456789.', tmp)
                    value = float(value)
                    max_value = max(max_value, value)
                    if max_value>=36.3 and max_value<=37.5:
                        result=u'正常'
                    elif max_value>37.5 and max_value<=38:
                        result=u'低热'
                    elif max_value >38 and max_value <=39:
                        result = u'中等温度'
                    elif max_value >39 and max_value <=41:
                        result = u'高热'
                    elif max_value >41:
                        result = u'超高热'
                    else:
                        pass
        except:
            pass
    #血压
    elif key=='blood_pressure':
        tmp_arr = value.split('/')
        if len(tmp_arr) == 2:
            try:
                if '-' in tmp_arr[0]:
                    maxArr = tmp_arr[0].split('-')
                    maxbp = maxArr[1]
                else:
                    maxbp = tmp_arr[0]
                if '-' in tmp_arr[1]:
                    minArr = tmp_arr[1].split('-')
                    minbp = minArr[1]
                else:
                    minbp = tmp_arr[1]
                maxbp = float(maxbp)
                minbp = float(minbp)
                if maxbp<90 and minbp<60:
                    result=u'低血压'
                elif (maxbp>=90 and maxbp<=139) or (minbp>=60 and minbp <=89):
                   result= u'正常'
                elif (maxbp >=140 and maxbp<=159) or (minbp >=90 and minbp<=99):
                    result= u'1级高血压'
                elif (maxbp >=160 and maxbp<=179) or (minbp >=100 and minbp<=109):
                    result= u'2级高血压'
                elif maxbp >=180 or minbp >=110:
                    result=u'3级高血压'
            except:
                pass
    #心率
    elif key=='heart_rate':
        value=float(value)
        try:
            if value> 100:
                result = u'心动过速'
            elif value > 60 and value <= 100:
                result = u'正常'
            elif value <= 60:
                result = u'心动过缓'
        except:
            pass
    #脉搏
    elif key == 'pulse':
        value=float(value)
        try:
            if value > 100:
                result = u'心动过速'
            elif value > 60 and value <= 100:
                result = u'正常'
            elif value <= 60:
                result = u'心动过缓'
        except:
            pass
    # 呼吸
    elif key == 'breath':
        value=float(value)
        try:
            if value > 20:
                result = u'呼吸快'
            elif value >=16 and value <=20:
                result = u'正常'
            elif value <16:
                result = u'呼吸慢'
        except:
            pass
    #收缩压
    elif key == 'systolic_pressure':
        value=float(value)
        try:
            if value<140:
                result = u'正常'
            elif value >=140 and value <=159:
                result = u'1级高血压'
            elif value>=160 and value<=179:
                 result=u'2级高血压'
            elif value>=180:
                result=u'3级高血压'
        except:
            pass
    #舒张压
    elif key == 'diastolic_pressure':
        value=float(value)
        try:
            if value<90:
                result=u'正常'
            elif value>=90 and value <=99:
                result=u'1级高血压'
            elif value >=100 and value <=109:
                result = u'2级高血压'
            elif value>=110:
                 result=u'3级高血压'
        except:
            pass
    return result

#同义症状名称替换
def normalized_symptomName(symptom_name):
    synonym_table = PATH + 'data/synonyms/symptomSynonym.txt'
    a = json.load(codecs.open(synonym_table, 'r', encoding='utf-8'))
    totalArr = []
    for k, v in a.items():
        tmpArr = []
        tmpArr.append(k)
        spliArr = v.split('@')
        for i in spliArr:
            i = i.strip('\n')
            tmpArr.append(i)
        totalArr.append(tmpArr)
    for i in totalArr:
        if symptom_name in i:
             return i[0]
    return symptom_name

#疾病同义名字替换：
def normalized_diseaseName(disease_name):
    BJCYYY_name2code_path = PATH+'data/synonyms/BJCYYY_name2code.txt'
    BJCYYY_name2code_dic = json.load(codecs.open(BJCYYY_name2code_path, 'r', encoding='utf-8'))
    if disease_name in BJCYYY_name2code_dic:
        return disease_name
    else:
        BJCYYY_name2code_old_path= PATH+'data/synonyms/BJCYYY_name2code_old.txt'
        BJCYYY_name2code_old_dic= json.load(codecs.open(BJCYYY_name2code_old_path, 'r', encoding='utf-8'))
        if disease_name in BJCYYY_name2code_old_dic:
            return disease_name
    return None

