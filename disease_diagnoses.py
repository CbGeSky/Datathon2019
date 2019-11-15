# 导入库
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import time

# 链接mimic
def get_data_MIMIC(sql):
    conn = psycopg2.connect(database='mimic',
                            user='postgres',
                            password='iamlog',
                            host='127.0.0.1',
                            port='5432')
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
# ----------------------诊断提取 11月14日
# 
# -- 统计特定疾病
path = 'SET search_path to mimiciii;'
query_diag1 ='''
WITH disease AS (
  SELECT na.hadm_id,COUNT(seq_num) AS icd_count FROM diagnoses_icd d
  INNER JOIN z_hyperna_full_patients na
  ON d.subject_id = na.subject_id AND d.hadm_id = na.hadm_id
  AND icd9_code IN ( '''
query_diag2 =''' )
  GROUP BY na.hadm_id )
SELECT 
  --na.subject_id, na.hadm_id, na.icustay_id, -- icd_count
  sum(CASE WHEN icd_count IS NOT NULL THEN 1 ELSE 0 END) AS diag
FROM z_hyperna_full_patients na
LEFT JOIN disease d
ON d.hadm_id = na.hadm_id
GROUP BY na.subject_id, na.hadm_id, na.icustay_id
ORDER BY na.subject_id, na.hadm_id, na.icustay_id;'''
query_disease_example = '''
WITH diabetes AS (
  SELECT na.hadm_id,COUNT(seq_num) AS icd_count FROM diagnoses_icd d
  INNER JOIN z_hyperna_full_patients na
  ON d.subject_id = na.subject_id AND d.hadm_id = na.hadm_id
  AND icd9_code IN (SELECT icd9_code FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%Diabetes%' AND LONG_TITLE NOT LIKE '%diabetes insipidus%' AND LONG_TITLE NOT LIKE '%pregnancy%'
  AND LONG_TITLE NOT LIKE '%Screening for diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Neonatal diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Family history%' )
  GROUP BY na.hadm_id )
SELECT 
  --na.subject_id, na.hadm_id, na.icustay_id, -- icd_count
  sum(CASE WHEN icd_count IS NOT NULL THEN 1 ELSE 0 END) AS diag
FROM z_hyperna_full_patients na
LEFT JOIN diabetes d
ON d.hadm_id = na.hadm_id
GROUP BY na.subject_id, na.hadm_id, na.icustay_id
ORDER BY na.subject_id, na.hadm_id, na.icustay_id;'''


query_diabetes =''' SELECT icd9_code FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%Diabetes%' AND LONG_TITLE NOT LIKE '%diabetes insipidus%' AND LONG_TITLE NOT LIKE '%pregnancy%'
  AND LONG_TITLE NOT LIKE '%Screening for diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Neonatal diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Family history%' 
  '''
query_cerebrovascular = ''' SELECT icd9_code FROM "d_icd_diagnoses" WHERE short_title ILIKE '%Cerebrovascular%' '''
query_liver = ''' SELECT icd9_code FROM "d_icd_diagnoses" WHERE short_title ILIKE '%liver%' and short_title not ilike '%deliver%' and long_title not ilike '%pregnancy%' '''
query_Coronary = '''SELECT icd9_code FROM "d_icd_diagnoses" WHERE short_title ILIKE '%Coronary%' '''
query_malignancy = '''SELECT icd9_code FROM "d_icd_diagnoses" WHERE short_title ILIKE '%malignancy%' '''

query_dementia = '''SELECT icd9_code FROM "d_icd_diagnoses" WHERE short_title ILIKE '%dementia%' '''
query_kidney = '''SELECT icd9_code FROM "d_icd_diagnoses"
  WHERE short_title ILIKE '%kidney%' and short_title not ilike '%study%' and short_title not ilike '%donor%' and short_title not ilike '%transplant%' and short_title not ilike '%exam%'
  and short_title not ilike '%malignancy%' and long_title not ilike '%delivery%' and long_title not ilike '%abortion%' '''
query_hyperlipidemia = '''SELECT icd9_code FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '% hyperlipidemia%' OR LONG_TITLE LIKE '%hypercholesterolemia%' '''
query_hypertension = '''SELECT icd9_code FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%hypertension%' AND LONG_TITLE NOT LIKE '%pregnancy%'
  AND LONG_TITLE NOT LIKE '%childbirth%' AND LONG_TITLE NOT LIKE '%puerperium%' AND LONG_TITLE NOT LIKE '%without%'
  AND LONG_TITLE NOT LIKE '%Portal hypertension%' AND LONG_TITLE NOT LIKE '%venous hypertension%' 
  AND LONG_TITLE NOT LIKE '%Screening for hypertension%' AND LONG_TITLE NOT LIKE '%Family history%' '''
query_pneumonia = '''SELECT icd9_code FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%pneumonia%' AND SHORT_TITLE NOT LIKE '%test%' AND SHORT_TITLE NOT LIKE '%exam%'
  AND SHORT_TITLE NOT LIKE '%cult%'AND SHORT_TITLE NOT LIKE '%histo%' AND SHORT_TITLE NOT LIKE '%unspec%'AND SHORT_TITLE NOT LIKE '%Meth%'
  AND SHORT_TITLE NOT LIKE '%Congenital%'AND SHORT_TITLE NOT LIKE '%Nd vac%'AND LONG_TITLE NOT LIKE '%vaccinaton%' '''

query_diarrhea = '''SELECT icd9_code FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%diarrhea%' AND SHORT_TITLE NOT LIKE '%agt%' OR SHORT_TITLE LIKE'%diarrhea%'
  AND SHORT_TITLE NOT LIKE '%Adv%' ''' 
query_infection = '''SELECT icd9_code FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%infection%' '''
query_respiratoryfailure = '''SELECT icd9_code FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%respiratory failure%' '''
query_sleepapnea = '''SELECT icd9_code FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%respiratory failure%' '''
query_Alkali = '''SELECT icd9_code FROM "mimiciii"."d_icd_diagnoses" WHERE "long_title" ILIKE '%alkali%'
  AND LONG_TITLE NOT LIKE '%Alkaline chemical burn%' AND LONG_TITLE NOT LIKE '% therapeutic use%' '''

query_Braininjury = '''SELECT icd9_code FROM d_icd_diagnoses WHERE "short_title" ILIKE '%Brain injury%'
  AND LONG_TITLE NOT LIKE '%Personal history%' '''
query_diabetesinsipidus = '''SELECT icd9_code FROM "d_icd_diagnoses" WHERE "long_title" ILIKE '%Diabetes insipidus%' '''
query_burn = '''SELECT icd9_code FROM "d_icd_diagnoses" WHERE "long_title" ILIKE '%burn%' 
  AND LONG_TITLE NOT LIKE '%Sunburn%'AND LONG_TITLE NOT LIKE '%friction burn%' '''
query_adrenal = '''SELECT icd9_code FROM "d_icd_diagnoses" WHERE "long_title" ILIKE '%adrenal%' 
  AND LONG_TITLE NOT LIKE '%neoplasm%' AND LONG_TITLE NOT LIKE '%newborn%'
  AND LONG_TITLE NOT LIKE '%Injury%' AND LONG_TITLE NOT LIKE '%Meningococc%' '''  
query_acidosis = '''SELECT icd9_code FROM "d_icd_diagnoses" WHERE "long_title" ILIKE '%acidosis%' 
  AND LONG_TITLE NOT LIKE '%juvenile type%'AND LONG_TITLE NOT LIKE '%newborn%' '''
  
query_heartfailure = '''SELECT icd9_code FROM "d_icd_diagnoses" WHERE short_title ILIKE '%heart failure%' '''
query_depression = '''SELECT icd9_code FROM "d_icd_diagnoses" WHERE "short_title" ILIKE '%depression%' 
  AND LONG_TITLE NOT LIKE '%newborn%' '''



name_diseases = ('diabetes','Coronary','malignancy','cerebrovascular','liver',
    'dementia','kidney','hyperlipidemia','hypertension','pneumonia',
    'diarrhea','infection','respiratoryfailure','sleepapnea','Alkali',
    'Braininjury','diabetesinsipidus','burn','adrenal','acidosis',
    'heartfailure','depression')

diag = pd.DataFrame(columns=name_diseases)

for i in range(22):
    name = 'query_'+ name_diseases[i]
    # print(path+eval(name))
    
    diag[name_diseases[i]] = get_data_MIMIC(path+query_diag1+ eval(name)+query_diag2)['diag']

#eval

diag.to_csv("./提取的数据/diagnoses.csv")  
print('debug')
