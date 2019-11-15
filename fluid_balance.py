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
query_colloid = '''
'''
query_crystall = '''
'''
query_vasopressor = '''
'''
query_sedative = '''
'''
query_drug_dose = '''
'''

name_input = ('colloid_vol','crystall_vol','vasopressor_flag','sedative_flag','drug_dose')
# 胶体液、晶体液、加压素、镇静剂、活性药物剂量
inputevents = pd.DataFrame(columns=name_input)

SELECT
  pvt.subject_id, pvt.hadm_id, pvt.icustay_id
  , SUM(colloid_bolus) as colloid_bolus
FROM