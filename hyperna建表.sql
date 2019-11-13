DROP TABLE IF EXISTS z_high_na_all;
CREATE TABLE z_high_na_all AS
SELECT 
--2330
  na.subject_id,na.hadm_id,icu.icustay_id,
  na.charttime_na_high,na.valuenum as na_high,
  icu.intime,icu.outtime
FROM
  (   
  SELECT 
  --raw02 raw01中有icu记录的 11537 -> 10192
    h.subject_id,h.hadm_id,
    h.charttime as charttime_na_high,lab.valuenum
  FROM
    (
      SELECT 
        subject_id,hadm_id,min(charttime) AS charttime
      --raw01 所有出现过钠过高的   11537
      --fixed03 修正为入lab48h后第一次出现高钠 count-> 2330 min()
      FROM mimiciii.labevents
      WHERE itemid = 50983  AND valuenum > 145 
      GROUP BY subject_id,hadm_id
    ) AS h
  INNER JOIN mimiciii.labevents lab
  ON h.subject_id=lab.subject_id AND h.hadm_id=lab.hadm_id
  AND lab.charttime = h.charttime
  AND lab.itemid = 50983
  ORDER BY subject_id,hadm_id
  ) AS na
INNER JOIN mimiciii.icustays icu
ON na.subject_id=icu.subject_id AND na.hadm_id=icu.hadm_id
AND icu.icustay_id IS NOT NULL 
AND (date_trunc('day',na.charttime_na_high) - INTERVAL '2' day) BETWEEN icu.intime AND icu.outtime
AND (date_trunc('day',na.charttime_na_high) + INTERVAL '2' day) BETWEEN icu.intime AND icu.outtime
ORDER BY subject_id,hadm_id,icustay_id;

---- 后向 backwards
DROP TABLE IF EXISTS z_hyperna_back;
CREATE TABLE z_hyperna_back AS
SELECT 
--2330
  b.subject_id,b.hadm_id,b.icustay_id,
  b.charttime_na_high,b.na_high,
  b.intime,b.outtime,
  b.charttime_last,lab.valuenum as na_back
FROM
  (
  SELECT 
    na.subject_id,na.hadm_id,na.icustay_id,
    na.charttime_na_high,na.na_high,na.intime,na.outtime,
    q.charttime_last
  FROM z_high_na_all na
  LEFT JOIN  
    (
      --raw 查找入icu后出现高钠往h后推 2天  的钠值 count-> 2283 min()
      SELECT 
        lab.subject_id,lab.hadm_id,max(lab.charttime) AS charttime_last --,lab.valuenum
      
      FROM mimiciii.labevents lab
      INNER JOIN mimiciii.z_high_na_all h
      ON lab.subject_id=h.subject_id AND lab.hadm_id=h.hadm_id AND lab.itemid = 50983 
      AND (date_trunc('day',lab.charttime)) 
      BETWEEN(date_trunc('day',h.charttime_na_high )+interval '1.5' day) AND ((date_trunc('day',h.charttime_na_high )+interval '2.9' day))  
      GROUP BY lab.subject_id,lab.hadm_id
    ) AS q
  ON na.subject_id=q.subject_id AND na.hadm_id=q.hadm_id
  ) as b
LEFT JOIN mimiciii.labevents lab
ON b.subject_id=lab.subject_id AND b.hadm_id=lab.hadm_id
AND lab.charttime = b.charttime_last
AND lab.itemid = 50983
ORDER BY subject_id,hadm_id,icustay_id;

---- 前向 forwards
DROP TABLE IF EXISTS z_hyperna_full;
CREATE TABLE z_hyperna_full AS
SELECT 

  b.subject_id,b.hadm_id,b.icustay_id, 
  b.intime,b.charttime_first,b.charttime_na_high,b.charttime_last,b.outtime,
  lab.valuenum as na_first,b.na_high,b.na_last
  -- count(b.subject_id)
FROM
  (
  SELECT 
    na.subject_id,na.hadm_id,na.icustay_id,
    na.charttime_na_high,na.na_high,na.intime,na.outtime,
    na.charttime_last,na.na_back as na_last,
    q.charttime_first
  FROM z_hyperna_back na
  LEFT JOIN  
    (
      --raw 查找入icu后出现高钠往前推 2天  的钠值 count-> 2283 min()
      SELECT 
        lab.subject_id,lab.hadm_id,min(lab.charttime) AS charttime_first --,lab.valuenum
      
      FROM mimiciii.labevents lab
      INNER JOIN mimiciii.z_high_na_all h
      ON lab.subject_id=h.subject_id AND lab.hadm_id=h.hadm_id AND lab.itemid = 50983 
      AND (date_trunc('day',lab.charttime)) 
      BETWEEN h.intime AND ((date_trunc('day',h.charttime_na_high )-interval '1.9' day))  
      GROUP BY lab.subject_id,lab.hadm_id
    ) AS q
  ON na.subject_id=q.subject_id AND na.hadm_id=q.hadm_id
  ) as b
LEFT JOIN mimiciii.labevents lab
ON b.subject_id=lab.subject_id AND b.hadm_id=lab.hadm_id
AND lab.charttime = b.charttime_first
AND lab.itemid = 50983
ORDER BY subject_id,hadm_id,icustay_id