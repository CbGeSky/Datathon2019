--排除准则
-- distinct hadm_id -> 18616
-- time -> 200s
-- 1、删除甲状和库欣
WITH diseases AS (
select * from diagnoses_icd
where icd9_code in ( SELECT icd9_code FROM d_icd_diagnoses
WHERE long_title ILIKE '%thyroiditis%' or  long_title ILIKE '%hyperparathyroidism%' 
or  long_title ILIKE '%hypothyroidism%' or  long_title ILIKE '%hyperthyroidism%' 
or long_title ILIKE '%Cushing%'  ) ),
-- 2、删除透析
dialysis AS (
SELECT subject_Id ,HADM_ID FROM chartevents WHERE ITEMID IN ( SELECT ITEMID 
FROM  d_items WHERE LABEL LIKE '%dialysis%' AND LINKSTO = 'chartevents' ) )

SELECT COUNT(DISTINCT hadm_id) FROM labevents la
WHERE itemid in ( 50983 ) AND hadm_id IS NOT NULL AND hadm_id IN
( SELECT hadm_id FROM icustays ic WHERE (ic.outtime - ic.intime) > interval '3d' )
AND hadm_id NOT IN (SELECT hadm_id FROM diseases) AND hadm_id NOT IN (SELECT hadm_id FROM dialysis)