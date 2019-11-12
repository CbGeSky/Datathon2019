-- first 提取高血钠患者
-- 1、icu入院内2天后出现高钠血
-- 2、高钠 > 145 27108 > 149 6739 
-- 3、fixed 修正为入icu48h后第一次出现高钠 count-> 2330
-- DROP IF EXISTS high_na_all
CREATE TABLE z_high_na_all AS
 
SELECT 
  h.subject_id,h.hadm_id,icu.icustay_id,
  h.charttime,
  icu.intime,icu.outtime
FROM
  (
    SELECT 
      lab.subject_id,lab.hadm_id,min(lab.charttime) AS charttime --,lab.valuenum
    --raw 所有出现过钠过高的
    --fixed 修正为入icu48h后第一次出现高钠 count-> 2330 min()
    FROM mimiciii.labevents lab
    WHERE lab.itemid = 50983 AND lab.valuenum > 145 
    GROUP BY lab.subject_id,lab.hadm_id --,lab.valuenum
  ) AS h
INNER JOIN mimiciii.icustays icu
ON h.subject_id=icu.subject_id AND h.hadm_id=icu.hadm_id
AND icu.icustay_id IS NOT NULL 
AND (date_trunc('day',h.charttime) - INTERVAL '2' day) BETWEEN icu.intime AND icu.outtime
AND (date_trunc('day',h.charttime) + INTERVAL '2' day) BETWEEN icu.intime AND icu.outtime
ORDER BY subject_id,hadm_id,icustay_id

-----------------------------------------------

SELECT 
  h.subject_id,h.hadm_id,h.icustay_id,
  h.charttime AS charttime_high,h.intime,h.outtime
FROM
(
  SELECT 
    lab.subject_id,lab.hadm_id,min(lab.charttime) AS charttime_first --,lab.valuenum
  --raw 查找入icu后出现高钠往前推一天的钠值 count-> 2330 min()
  FROM mimiciii.labevents lab
  INNER JOIN mimiciii.z_highna_all h
  ON lab.subject_id=h.subject_id AND lab.hadm_id=h.hadm_id AND lab.itemid = 50983 
  AND (date_trunc('day',lab.charttime)) BETWEEN h.intime AND (date_trunc('day',h.charttime )-interval '1' day)  
  GROUP BY lab.subject_id,lab.hadm_id
) AS q

  SELECT 
    lab.subject_id,lab.hadm_id,max(lab.charttime) AS charttime_first --,lab.valuenum
  --raw 查找入icu后出现高钠往前推一天的钠值 count-> 2330 min()
  FROM mimiciii.labevents lab
  INNER JOIN mimiciii.z_highna_all h
  ON lab.subject_id=h.subject_id AND lab.hadm_id=h.hadm_id AND lab.itemid = 50983 
  AND (date_trunc('day',lab.charttime)) BETWEEN(date_trunc('day',h.charttime )+interval '1' day) AND h.outtime  
  GROUP BY lab.subject_id,lab.hadm_id