# 导入库
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import time

# 链接mimic
def get_data_MIMIC(sql):
    conn = psycopg2.connect(database=mountedDB['mimic7601']['database'],
                            user=mountedDB['mimic7601']['username'],
                            password=mountedDB['mimic7601']['password'],
                            host=mountedDB['mimic7601']['host'],
                            port=mountedDB['mimic7601']['port'])
    cur = conn.cursor()
    try:
        cur.execute(sql)
        #获取表的所有字段名称
        coloumns = [row[0] for row in cur.description]
        result = [[str(item) for item in row] for row in cur.fetchall()]
        return pd.DataFrame(result,columns=coloumns)
    except Exception as ex:
        print(ex)
    finally:
        conn.close()

# tab1从diagnoses_icd表查询出所有心衰病人的住院ID，心衰的诊断顺序在第一个
# tab2从admissions LEFT JOIN patients表查询出性别，年龄，住院总天数
#连接tab1和tab2，得到心衰病人的患者ID，住院ID，性别，年龄，住院总天数
sql='''
CREATE TEMP TABLE tab1 AS
SELECT DISTINCT HADM_ID
FROM diagnoses_icd 
WHERE CAST( SEQ_NUM AS integer ) <  2 AND ICD9_CODE IN
      (SELECT ICD9_CODE 
			 FROM d_icd_diagnoses 
       WHERE LONG_TITLE LIKE '%heart failure%' AND LONG_TITLE not LIKE '%without%');

CREATE TEMP TABLE tab2 AS
(SELECT admissions.SUBJECT_ID,admissions.HADM_ID, patients.GENDER,
CAST(EXTRACT(YEAR from age(date(admissions.ADMITTIME),date(patients.DOB))) AS integer) AS P_AGE,
CAST(EXTRACT(DAY from age(date(admissions.DISCHTIME),date(admissions.ADMITTIME)))AS integer)+
CAST(EXTRACT(MONTH from age(date(admissions.DISCHTIME),date(admissions.ADMITTIME)))AS integer)*30 AS T_HOSP_DAY
FROM admissions LEFT JOIN patients
ON admissions.SUBJECT_ID = patients.SUBJECT_ID) ;

SELECT tab2.SUBJECT_ID,tab2.HADM_ID,tab2.GENDER,tab2.P_AGE,tab2.T_HOSP_DAY
FROM tab1 LEFT JOIN tab2
ON tab1.HADM_ID=tab2.HADM_ID;
'''
data1=get_data_MIMIC(sql)

#增加列
df = pd.DataFrame(data1)
df['cardiomyopathy']=0
df['valve']=0
df['atrial flutter or atrial fibrillation']=0
df['hyperlipidemia']=0
df['hypertension']=0
df['diabetes']=0
df['sleep apnea']=0
df['anemia']=0
df['infection']=0
df['chronic kidney disease']=0

#查询出各疾病对应ID
#心肌病
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%cardiomyopathy%' OR LONG_TITLE LIKE '%cardiomyopathies%';'''
cardiomyopathy=get_data_MIMIC(sql)
#瓣膜病
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%valve%' ;'''
valve=get_data_MIMIC(sql)
#心房纤颤或心房扑动
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%Atrial flutter%' OR LONG_TITLE LIKE '%Atrial fibrillation%';'''
atrial_flutter=get_data_MIMIC(sql)
#高脂血症
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '% hyperlipidemia%' OR LONG_TITLE LIKE '%hypercholesterolemia%' OR LONG_TITLE LIKE '%hyperglyceridemia%';'''
hyperlipidemia=get_data_MIMIC(sql)
#高血压
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%hypertension%' AND LONG_TITLE NOT LIKE '%pregnancy%'
AND LONG_TITLE NOT LIKE '%childbirth%' AND LONG_TITLE NOT LIKE '%puerperium%' AND LONG_TITLE NOT LIKE '%without%'
AND LONG_TITLE NOT LIKE '%Portal hypertension%' AND LONG_TITLE NOT LIKE '%venous hypertension%' 
AND LONG_TITLE NOT LIKE '%Screening for hypertension%' AND LONG_TITLE NOT LIKE '%Family history%';'''
hypertension=get_data_MIMIC(sql)
#糖尿病
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%Diabetes%' AND LONG_TITLE NOT LIKE '%diabetes insipidus%' AND LONG_TITLE NOT LIKE '%pregnancy%'
AND LONG_TITLE NOT LIKE '%Screening for diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Neonatal diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Family history%' ;'''
diabetes=get_data_MIMIC(sql)
#睡眠呼吸暂停
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%sleep apnea%' ;'''
sleep_apnea=get_data_MIMIC(sql)
#贫血
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%anemia%'AND LONG_TITLE NOT LIKE '%Anemia of mother%' AND LONG_TITLE NOT LIKE '%Anemia of prematurity%'
AND LONG_TITLE NOT LIKE '%Screening%' AND LONG_TITLE NOT LIKE '%Family history%';'''
anemia=get_data_MIMIC(sql)
#感染
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%infection%' ;'''
infection=get_data_MIMIC(sql)
#肾功能不全
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%Chronic kidney disease%' OR LONG_TITLE LIKE '%End stage renal disease%';'''
kidney_disease=get_data_MIMIC(sql)

#根据心衰病人住院ID从diagnoses_icd表得到该病人所有住院代码ICD9_CODE
sql='''SELECT  HADM_ID,ICD9_CODE
FROM diagnoses_icd 
WHERE  HADM_ID IN
(SELECT DISTINCT HADM_ID
FROM diagnoses_icd 
WHERE CAST( SEQ_NUM AS integer ) <  2 AND ICD9_CODE IN
      (SELECT ICD9_CODE 
			 FROM d_icd_diagnoses 
       WHERE LONG_TITLE LIKE '%heart failure%' AND LONG_TITLE not LIKE '%without%')

)
ORDER BY HADM_ID;'''
HADM_ICD9=get_data_MIMIC(sql)
df_ICD9 = pd.DataFrame(HADM_ICD9)

#将心衰病人是否患有心肌病，瓣膜病，···，肾功能不全 写入df表
j=0
idlist=[]
hadmid=df["hadm_id"][j]
for i in range(df_ICD9.shape[0]):#df_ICD9.shape[0]
    if df_ICD9["hadm_id"][i]==hadmid:
        idlist.append(df_ICD9["icd9_code"][i])
    else:
        if len([x for x in idlist if x in list(cardiomyopathy["icd9_code"])])!=0:
            df.loc[j,'cardiomyopathy']=1
        if len([x for x in idlist if x in list(valve["icd9_code"])])!=0:
            df.loc[j,'valve']=1
        if len([x for x in idlist if x in list(atrial_flutter["icd9_code"])])!=0:
            df.loc[j,'atrial flutter or atrial fibrillation']=1
        if len([x for x in idlist if x in list(hyperlipidemia["icd9_code"])])!=0:
            df.loc[j,'hyperlipidemia']=1
        if len([x for x in idlist if x in list(hypertension["icd9_code"])])!=0:
            df.loc[j,'hypertension']=1
        if len([x for x in idlist if x in list(diabetes["icd9_code"])])!=0:
            df.loc[j,'diabetes']=1
        if len([x for x in idlist if x in list(sleep_apnea["icd9_code"])])!=0:
            df.loc[j,'sleep apnea']=1
        if len([x for x in idlist if x in list(anemia["icd9_code"])])!=0:
            df.loc[j,'anemia']=1
        if len([x for x in idlist if x in list(infection["icd9_code"])])!=0:
            df.loc[j,'infection']=1
        if len([x for x in idlist if x in list(kidney_disease["icd9_code"])])!=0:
            df.loc[j,'chronic kidney disease']=1
        j=j+1
        hadmid=df["hadm_id"][j]
        idlist.clear()

#根据病人住院总天数t_hosp_day为df表增加相应行
for j in range(1639):#df.shape[0]=1639
    for i in range(int(df["t_hosp_day"][j])):
        s = pd.Series({'subject_id':df["subject_id"][j], 'hadm_id':df["hadm_id"][j],
        'gender':df["gender"][j],'p_age':df["p_age"][j],'cardiomyopathy':df["cardiomyopathy"][j],
        'valve':df["valve"][j],'atrial flutter or atrial fibrillation':df["atrial flutter or atrial fibrillation"][j],
        'hyperlipidemia':df["hyperlipidemia"][j],
        'hypertension':df["hypertension"][j],'diabetes':df["diabetes"][j],'sleep apnea':df["sleep apnea"][j],
        'anemia':df["anemia"][j],'infection':df["infection"][j],
        'chronic kidney disease':df["chronic kidney disease"][j],
        't_hosp_day':i})
        df = df.append(s, ignore_index=True)

#根据住院ID和住院天数（t_hosp_day在这不是总天数了）将df表排序，排序后重新设置索引
df=df.sort_values(by=['hadm_id','t_hosp_day'],ascending=(True,True))
df=df.reset_index(drop=True)

#tab3
#根据心衰病人住院ID从labevents 表查询出
#（脑利钠肽前体	血清尿酸	中性粒细胞	二氧化碳 血氧	尿素 总胆红素	总蛋白	无机磷	氯化物 红细胞比积测定	肌酐	肌钙蛋白T
#  葡萄糖	血小板计数	血浆D二聚体测定	血清白蛋白	钙（50893	50808	）	钠（50824	50983	）	钾（50971	50822）	镁）的所有记录
#tab4
#根据心衰病人住院ID从chartevents表查询出 （呼吸 脉搏（心率） 血低压  血高压  体温（））
#备注体温是摄氏度，脉搏用心理代替  ,呼吸塑料采取的是自发呼吸速率
#将tab4插入tab3，并连接admission表得到心衰病人住院ID，项目id，项目所做检查天数，项目检查值
#将t_hosp_day转为int，方便排序
#据住院ID和t_hosp_day将df_LAB_CHART表排序，重新设置索引（排序是为了方便写入df表，少一层循环）
sql='''
CREATE TEMPORARY TABLE tab3 AS(
SELECT HADM_ID,ITEMID,CHARTTIME,VALUENUM FROM  labevents
WHERE HADM_ID IN ( SELECT HADM_ID
					FROM diagnoses_icd 
					WHERE	CAST( SEQ_NUM AS integer ) <  2 
					AND ICD9_CODE IN (SELECT ICD9_CODE 
									  FROM d_icd_diagnoses 
									  WHERE LONG_TITLE LIKE '%heart failure%' 
                                      AND LONG_TITLE not LIKE '%without%'
                                      )
                  )      
AND(ITEMID='50963' OR 	ITEMID='51007' OR 	ITEMID='51256' OR 	ITEMID='50804' OR 	ITEMID='50817' OR 	ITEMID='51006' 
OR 	ITEMID='50885' OR 	ITEMID='50976' OR 	ITEMID='50970' OR 	ITEMID='50902' OR 	ITEMID='51221' OR 	ITEMID='50912' 
OR 	ITEMID='51003' OR 	ITEMID='50931' OR 	ITEMID='51265' OR 	ITEMID='50915' OR 	ITEMID='50862' OR 	ITEMID='50893'
OR 	ITEMID='50808' OR 	ITEMID='50824' OR 	ITEMID='50983' OR 	ITEMID='50971' OR 	ITEMID='50822' OR 	ITEMID='50960' )
ORDER BY HADM_ID              );

CREATE TEMPORARY TABLE tab4 AS(
SELECT HADM_ID,ITEMID,CHARTTIME,VALUENUM FROM  chartevents
WHERE HADM_ID IN ( SELECT HADM_ID
					FROM diagnoses_icd 
					WHERE	CAST( SEQ_NUM AS integer ) <  2 
					AND ICD9_CODE IN (SELECT ICD9_CODE 
									  FROM d_icd_diagnoses 
									  WHERE LONG_TITLE LIKE '%heart failure%' 
                                      AND LONG_TITLE not LIKE '%without%'
                                      )
                  )      
AND (ITEMID='224689' OR 	ITEMID='220045' OR 	ITEMID='223751' OR 	ITEMID='223752' OR 	ITEMID='223762' )
ORDER BY HADM_ID                );

INSERT INTO tab3 SELECT * FROM tab4;

SELECT tab3.HADM_ID,tab3.ITEMID,
(CAST(EXTRACT(DAY from age(date(tab3.CHARTTIME),date(admissions.ADMITTIME))) AS integer )+CAST(EXTRACT(MONTH from age(date(tab3.CHARTTIME),date(admissions.ADMITTIME))) AS integer )*30) AS T_HOSP_DAY,AVG(tab3.VALUENUM) AS VALUE 
FROM tab3 LEFT JOIN admissions
ON tab3.HADM_ID=admissions.HADM_ID
GROUP BY tab3.HADM_ID,tab3.ITEMID,
CAST(EXTRACT(DAY from age(date(tab3.CHARTTIME),date(admissions.ADMITTIME))) AS integer )+CAST(EXTRACT(MONTH from age(date(tab3.CHARTTIME),date(admissions.ADMITTIME))) AS integer )*30
'''
LAB_CHART=get_data_MIMIC(sql)
df_LAB_CHART = pd.DataFrame(LAB_CHART)
df_LAB_CHART['t_hosp_day'] = df_LAB_CHART['t_hosp_day'].str.replace(',','').astype(int)
df_LAB_CHART=df_LAB_CHART.sort_values(by=['hadm_id','t_hosp_day'],ascending=(True,True))
df_LAB_CHART=df_LAB_CHART.reset_index(drop=True)

#增加列
df['脑利钠肽前体']=0
df['血清尿酸']=0
df['中性粒细胞']=0
df['二氧化碳']=0
df['血氧']=0
df['尿素']=0
df['总胆红素']=0
df['总蛋白']=0
df['无机磷']=0
df['氯化物']=0
df['红细胞比积测定']=0
df['肌酐']=0
df['肌钙蛋白']=0
df['葡萄糖']=0
df['血小板计数']=0
df['血浆d二聚体测定']=0
df['血清白蛋白']=0
df['钙']=0
df['钠']=0
df['钾']=0
df['镁']=0

#df_LAB_CHART表和df表都是排序好的，可用一层循环进行转换
j=0
for i in range(df_LAB_CHART.shape[0]):
    if int(df_LAB_CHART["t_hosp_day"][i])<0:#排除检查时间小于入院时间的记录
        continue
    if j<df.shape[0]-1:#排除检查时间大于出院时间的记录
        if (df_LAB_CHART["hadm_id"][i]==df["hadm_id"][j]) and (int(df_LAB_CHART["t_hosp_day"][i]) != int(df["t_hosp_day"][j]) ) and (df_LAB_CHART["hadm_id"][i]!=df["hadm_id"][j+1]):
            continue
    while True:
        if (df_LAB_CHART["hadm_id"][i]!=df["hadm_id"][j] or int(df_LAB_CHART["t_hosp_day"][i])!=int(df["t_hosp_day"][j]))and j<df.shape[0]-1:
            j=j+1
        else:
            break
    if df_LAB_CHART["itemid"][i] == '50963':
        df.loc[j,'脑利钠肽前体']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51007':
        df.loc[j,'血清尿酸']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51256':
        df.loc[j,'中性粒细胞']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50804':
        df.loc[j,'二氧化碳']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50817':
        df.loc[j,'血氧']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51006':
        df.loc[j,'尿素']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50885':
        df.loc[j,'总胆红素']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50976':
        df.loc[j,'总蛋白']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50970':
        df.loc[j,'无机磷']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50902':
        df.loc[j,'氯化物']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51221':
        df.loc[j,'红细胞比积测定']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50912':
        df.loc[j,'肌酐']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51003':
        df.loc[j,'肌钙蛋白']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50931':
        df.loc[j,'葡萄糖']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51265':
        df.loc[j,'血小板计数']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50915':
        df.loc[j,'血浆d二聚体测定']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50862':
        df.loc[j,'血清白蛋白']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50893' or df_LAB_CHART["itemid"][i] == '50808':
        df.loc[j,'钙']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50824' or df_LAB_CHART["itemid"][i] == '50983':
        df.loc[j,'钠']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50971' or df_LAB_CHART["itemid"][i] == '50822':
        df.loc[j,'钾']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50960':
        df.loc[j,'镁']=df_LAB_CHART["value"][i]
print(df)
