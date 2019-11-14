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
query_cad = '''
WITH cad AS (
  SELECT na.hadm_id,COUNT(seq_num) AS icd_count FROM diagnoses_icd d
  INNER JOIN z_hyperna_full_patients na
  ON d.subject_id = na.subject_id AND d.hadm_id = na.hadm_id
  AND icd9_code IN (SELECT icd9_code FROM "d_icd_diagnoses" WHERE short_title ILIKE '%Coronary%')
  GROUP BY na.hadm_id )
SELECT 
  --na.subject_id, na.hadm_id, na.icustay_id, -- icd_count
  sum(CASE WHEN icd_count IS NOT NULL THEN 1 ELSE 0 END) AS diag
FROM z_hyperna_full_patients na
LEFT JOIN cad d
ON d.hadm_id = na.hadm_id
GROUP BY na.subject_id, na.hadm_id, na.icustay_id
ORDER BY na.subject_id, na.hadm_id, na.icustay_id;'''
query_magligtumor = '''
WITH disease AS (
  SELECT na.hadm_id,COUNT(seq_num) AS icd_count FROM diagnoses_icd d
  INNER JOIN z_hyperna_full_patients na
  ON d.subject_id = na.subject_id AND d.hadm_id = na.hadm_id
  AND icd9_code IN (SELECT icd9_code "d_icd_diagnoses" WHERE short_title ILIKE '%malignancy%')
  GROUP BY na.hadm_id )
SELECT 
  --na.subject_id, na.hadm_id, na.icustay_id, -- icd_count
  sum(CASE WHEN icd_count IS NOT NULL THEN 1 ELSE 0 END) AS diag
FROM z_hyperna_full_patients na
LEFT JOIN disease d
ON d.hadm_id = na.hadm_id
GROUP BY na.subject_id, na.hadm_id, na.icustay_id
ORDER BY na.subject_id, na.hadm_id, na.icustay_id;'''
query_diabetes =''' SELECT icd9_code FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%Diabetes%' AND LONG_TITLE NOT LIKE '%diabetes insipidus%' AND LONG_TITLE NOT LIKE '%pregnancy%'
  AND LONG_TITLE NOT LIKE '%Screening for diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Neonatal diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Family history%' )
  GROUP BY na.hadm_id '''
query_cerebrovascular = ''' SELECT icd9_code FROM "d_icd_diagnoses" WHERE short_title ILIKE '%Cerebrovascular%' '''
query_liver = ''' SELECT icd9_code FROM "d_icd_diagnoses" WHERE (short_title ILIKE '%liver%' and short_title not ilike '%deliver%' and long_title not ilike '%pregnancy%') '''
name_diseases = ('diabetes','cad','magligtumor','cerebrovascular','liver',
    'dementia','kidney','hyperlipidemia','hypertension','pneumonia',
    'diarrhea','infection','respiratory failure','abnormal breathing and sleep','Alkali poisoning',
    'Brain injury','Diabetes insipidus','burn','adrenal dysfunction','acidosis',
    'heart failure','depression')
diag = pd.DataFrame(columns=name_diseases)
diag[name_diseases[3]] = get_data_MIMIC(path+query_diag1+query_cerebrovascular+query_diag2)['diag']
diag[name_diseases[4]] = get_data_MIMIC(path+query_diag1+query_liver+query_diag2)['diag']
print(diag.head())
print('debug')

