
--删除甲状和库欣
CREATE TABLE thyroid AS
select * from diagnoses_icd
where icd9_code in(
SELECT icd9_code FROM d_icd_diagnoses
WHERE long_title ILIKE '%thyroiditis%' or  long_title ILIKE '%hyperparathyroidism%' or  long_title ILIKE '%hypothyroidism%' or  long_title ILIKE '%hyperthyroidism%' or long_title ILIKE '%Cushing%'  )

delete from z_hyperna_full_patients
where subject_id in (
				 select z_hyperna_full_patients.subject_id
				 from z_hyperna_full_patients,thyroid
				 where z_hyperna_full_patients.subject_id=thyroid.subject_id and z_hyperna_full_patients.hadm_id=thyroid.hadm_id
)

--删除透析
CREATE TABLE touxi AS
SELECT subject_Id ,HADM_ID FROM chartevents WHERE ITEMID IN
(
SELECT ITEMID FROM  d_items WHERE LABEL LIKE '%dialysis%' AND LINKSTO = 'chartevents'
);


delete from z_hyperna_full_patients
where subject_id in (
				 select z_hyperna_full_patients.subject_id
				 from z_hyperna_full_patients,touxi
				 where z_hyperna_full_patients.subject_id=touxi.subject_id and z_hyperna_full_patients.hadm_id=touxi.hadm_id
)