-- extract data
-- na in table labitems itemid=50983
SET search_path to mimiciii;
SELECT 
  subject_id,hadm_id,min(charttime) as chartime_new,valuenum

FROM labevents

where itemid = 50983 and valuenum > 145 
GROUP BY subject_id,hadm_id,valuenum limit 100 ;

-- http://www.voidcn.com/article/p-vleioxic-bsk.html
-- group by 聚合函数问题解决，需要加一次自身连接
SELECT 
--2330
  na.subject_id,na.hadm_id,icu.icustay_id,
  na.charttime_na_high,na.valuenum as na_high,
  icu.intime,icu.outtime
FROM
  (  -- 10912
  SELECT 
    h.subject_id,h.hadm_id,
    h.charttime as charttime_na_high,lab.valuenum
  FROM
    (
      SELECT 
        subject_id,hadm_id,min(charttime) AS charttime
      --raw 所有出现过钠过高的
      --fixed 修正为入lab48h后第一次出现高钠 count-> 2330 min()
      FROM mimiciii.labevents
      WHERE itemid = 50983 AND valuenum > 145 
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
ORDER BY subject_id,hadm_id,icustay_id