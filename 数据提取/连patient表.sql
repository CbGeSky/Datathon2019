
CREATE TABLE z_hyperna_full_patients AS
select z.subject_id,z.hadm_id,z.icustay_id,
z.intime,z.charttime_first,z.charttime_na_high,z.charttime_last,z.outtime,
z.na_first,z.na_high,z.na_last,
pa.gender, pa.dob,pa.dod,(EXTRACT(year FROM  z.charttime_first)-EXTRACT(year FROM  pa.dob)) as age
from z_hyperna_full z
inner join patients pa
on z.subject_id=pa.subject_id and EXTRACT(year FROM  z.charttime_first)-EXTRACT(year FROM  pa.dob)>18

update z_hyperna_full_patients
set age=90
where age>90