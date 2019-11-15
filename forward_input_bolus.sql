-- This query pivots lab values-- This query pivots lab values 
-- labevents between charttime_na_high and charttime_last
-- CREATE materialized VIEW labsfirstday AS
SELECT
  pvt.subject_id, pvt.hadm_id, pvt.icustay_id

  , SUM(CASE WHEN colloid_bolus IS NOT NULL THEN colloid_bolus ELSE 0 END) as colloid_bolus

FROM
( -- begin query that extracts the data
  SELECT ie.subject_id, ie.hadm_id, ie.icustay_id,le.colloid_bolus
  FROM z_hyperna_full_patients ie

  LEFT JOIN z_colloid_bolus le
    ON le.icustay_id = ie.icustay_id
    -- AND le.charttime BETWEEN (ie.charttime_first ) AND (ie.charttime_na_high)
    AND le.charttime BETWEEN (ie.charttime_na_high ) AND (ie.charttime_last)
) pvt
GROUP BY pvt.subject_id, pvt.hadm_id, pvt.icustay_id
ORDER BY pvt.subject_id, pvt.hadm_id, pvt.icustay_id;

SELECT
  pvt.subject_id, pvt.hadm_id, pvt.icustay_id

  , SUM(CASE WHEN crystalloid_bolus IS NOT NULL THEN crystalloid_bolus ELSE 0 END) as crystalloid_bolus

FROM
( -- begin query that extracts the data
  SELECT ie.subject_id, ie.hadm_id, ie.icustay_id,le.crystalloid_bolus
  FROM z_hyperna_full_patients ie

  LEFT JOIN z_crystalloid_bolus le
    ON le.icustay_id = ie.icustay_id
    -- AND le.charttime BETWEEN (ie.charttime_first ) AND (ie.charttime_na_high)
    AND le.charttime BETWEEN (ie.charttime_na_high ) AND (ie.charttime_last)
) pvt
GROUP BY pvt.subject_id, pvt.hadm_id, pvt.icustay_id
ORDER BY pvt.subject_id, pvt.hadm_id, pvt.icustay_id;
