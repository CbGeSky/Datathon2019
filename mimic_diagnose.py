# �����
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import time

# ����mimic
def get_data_MIMIC(sql):
    conn = psycopg2.connect(database=mountedDB['mimic7601']['database'],
                            user=mountedDB['mimic7601']['username'],
                            password=mountedDB['mimic7601']['password'],
                            host=mountedDB['mimic7601']['host'],
                            port=mountedDB['mimic7601']['port'])
    cur = conn.cursor()
    try:
        cur.execute(sql)
        #��ȡ��������ֶ�����
        coloumns = [row[0] for row in cur.description]
        result = [[str(item) for item in row] for row in cur.fetchall()]
        return pd.DataFrame(result,columns=coloumns)
    except Exception as ex:
        print(ex)
    finally:
        conn.close()

# tab1��diagnoses_icd���ѯ��������˥���˵�סԺID����˥�����˳���ڵ�һ��
# tab2��admissions LEFT JOIN patients���ѯ���Ա����䣬סԺ������
#����tab1��tab2���õ���˥���˵Ļ���ID��סԺID���Ա����䣬סԺ������
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

#������
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

#��ѯ����������ӦID
#�ļ���
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%cardiomyopathy%' OR LONG_TITLE LIKE '%cardiomyopathies%';'''
cardiomyopathy=get_data_MIMIC(sql)
#��Ĥ��
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%valve%' ;'''
valve=get_data_MIMIC(sql)
#�ķ��˲����ķ��˶�
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%Atrial flutter%' OR LONG_TITLE LIKE '%Atrial fibrillation%';'''
atrial_flutter=get_data_MIMIC(sql)
#��֬Ѫ֢
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '% hyperlipidemia%' OR LONG_TITLE LIKE '%hypercholesterolemia%' OR LONG_TITLE LIKE '%hyperglyceridemia%';'''
hyperlipidemia=get_data_MIMIC(sql)
#��Ѫѹ
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%hypertension%' AND LONG_TITLE NOT LIKE '%pregnancy%'
AND LONG_TITLE NOT LIKE '%childbirth%' AND LONG_TITLE NOT LIKE '%puerperium%' AND LONG_TITLE NOT LIKE '%without%'
AND LONG_TITLE NOT LIKE '%Portal hypertension%' AND LONG_TITLE NOT LIKE '%venous hypertension%' 
AND LONG_TITLE NOT LIKE '%Screening for hypertension%' AND LONG_TITLE NOT LIKE '%Family history%';'''
hypertension=get_data_MIMIC(sql)
#����
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%Diabetes%' AND LONG_TITLE NOT LIKE '%diabetes insipidus%' AND LONG_TITLE NOT LIKE '%pregnancy%'
AND LONG_TITLE NOT LIKE '%Screening for diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Neonatal diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Family history%' ;'''
diabetes=get_data_MIMIC(sql)
#˯�ߺ�����ͣ
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%sleep apnea%' ;'''
sleep_apnea=get_data_MIMIC(sql)
#ƶѪ
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%anemia%'AND LONG_TITLE NOT LIKE '%Anemia of mother%' AND LONG_TITLE NOT LIKE '%Anemia of prematurity%'
AND LONG_TITLE NOT LIKE '%Screening%' AND LONG_TITLE NOT LIKE '%Family history%';'''
anemia=get_data_MIMIC(sql)
#��Ⱦ
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%infection%' ;'''
infection=get_data_MIMIC(sql)
#�����ܲ�ȫ
sql='''SELECT ICD9_CODE FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%Chronic kidney disease%' OR LONG_TITLE LIKE '%End stage renal disease%';'''
kidney_disease=get_data_MIMIC(sql)

#������˥����סԺID��diagnoses_icd��õ��ò�������סԺ����ICD9_CODE
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

#����˥�����Ƿ����ļ�������Ĥ�����������������ܲ�ȫ д��df��
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

#���ݲ���סԺ������t_hosp_dayΪdf��������Ӧ��
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

#����סԺID��סԺ������t_hosp_day���ⲻ���������ˣ���df�����������������������
df=df.sort_values(by=['hadm_id','t_hosp_day'],ascending=(True,True))
df=df.reset_index(drop=True)

#tab3
#������˥����סԺID��labevents ���ѯ��
#����������ǰ��	Ѫ������	������ϸ��	������̼ Ѫ��	���� �ܵ�����	�ܵ���	�޻���	�Ȼ��� ��ϸ���Ȼ��ⶨ	����	���Ƶ���T
#  ������	ѪС�����	Ѫ��D������ⶨ	Ѫ��׵���	�ƣ�50893	50808	��	�ƣ�50824	50983	��	�أ�50971	50822��	þ�������м�¼
#tab4
#������˥����סԺID��chartevents���ѯ�� ������ ���������ʣ� Ѫ��ѹ  Ѫ��ѹ  ���£�����
#��ע���������϶ȣ��������������  ,�������ϲ�ȡ�����Է���������
#��tab4����tab3��������admission��õ���˥����סԺID����Ŀid����Ŀ���������������Ŀ���ֵ
#��t_hosp_dayתΪint����������
#��סԺID��t_hosp_day��df_LAB_CHART��������������������������Ϊ�˷���д��df����һ��ѭ����
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

#������
df['��������ǰ��']=0
df['Ѫ������']=0
df['������ϸ��']=0
df['������̼']=0
df['Ѫ��']=0
df['����']=0
df['�ܵ�����']=0
df['�ܵ���']=0
df['�޻���']=0
df['�Ȼ���']=0
df['��ϸ���Ȼ��ⶨ']=0
df['����']=0
df['���Ƶ���']=0
df['������']=0
df['ѪС�����']=0
df['Ѫ��d������ⶨ']=0
df['Ѫ��׵���']=0
df['��']=0
df['��']=0
df['��']=0
df['þ']=0

#df_LAB_CHART���df��������õģ�����һ��ѭ������ת��
j=0
for i in range(df_LAB_CHART.shape[0]):
    if int(df_LAB_CHART["t_hosp_day"][i])<0:#�ų����ʱ��С����Ժʱ��ļ�¼
        continue
    if j<df.shape[0]-1:#�ų����ʱ����ڳ�Ժʱ��ļ�¼
        if (df_LAB_CHART["hadm_id"][i]==df["hadm_id"][j]) and (int(df_LAB_CHART["t_hosp_day"][i]) != int(df["t_hosp_day"][j]) ) and (df_LAB_CHART["hadm_id"][i]!=df["hadm_id"][j+1]):
            continue
    while True:
        if (df_LAB_CHART["hadm_id"][i]!=df["hadm_id"][j] or int(df_LAB_CHART["t_hosp_day"][i])!=int(df["t_hosp_day"][j]))and j<df.shape[0]-1:
            j=j+1
        else:
            break
    if df_LAB_CHART["itemid"][i] == '50963':
        df.loc[j,'��������ǰ��']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51007':
        df.loc[j,'Ѫ������']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51256':
        df.loc[j,'������ϸ��']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50804':
        df.loc[j,'������̼']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50817':
        df.loc[j,'Ѫ��']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51006':
        df.loc[j,'����']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50885':
        df.loc[j,'�ܵ�����']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50976':
        df.loc[j,'�ܵ���']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50970':
        df.loc[j,'�޻���']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50902':
        df.loc[j,'�Ȼ���']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51221':
        df.loc[j,'��ϸ���Ȼ��ⶨ']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50912':
        df.loc[j,'����']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51003':
        df.loc[j,'���Ƶ���']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50931':
        df.loc[j,'������']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '51265':
        df.loc[j,'ѪС�����']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50915':
        df.loc[j,'Ѫ��d������ⶨ']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50862':
        df.loc[j,'Ѫ��׵���']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50893' or df_LAB_CHART["itemid"][i] == '50808':
        df.loc[j,'��']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50824' or df_LAB_CHART["itemid"][i] == '50983':
        df.loc[j,'��']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50971' or df_LAB_CHART["itemid"][i] == '50822':
        df.loc[j,'��']=df_LAB_CHART["value"][i]
        continue
    if  df_LAB_CHART["itemid"][i] == '50960':
        df.loc[j,'þ']=df_LAB_CHART["value"][i]
print(df)
