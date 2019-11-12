-- extract data
-- na in table labitems itemid=50983
SET search_path to mimiciii;
SELECT 
  subject_id,hadm_id,min(charttime) as chartime_new,valuenum

FROM labevents

where itemid = 50983 and valuenum > 145 
GROUP BY subject_id,hadm_id,valuenum limit 100 ;
