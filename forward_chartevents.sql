-- This query pivots lab values taken in the first 24 hours of a patient's stay

-- Have already confirmed that the unit of measurement is always the same: null or the correct unit

-- DROP MATERIALIZED VIEW IF EXISTS labsfirstday CASCADE;
-- CREATE materialized VIEW labsfirstday AS
SELECT
  pvt.subject_id, pvt.hadm_id, pvt.icustay_id

  , AVG(CASE WHEN label = 'Mask Ventilation (Intubation)' THEN valuenum ELSE null END) as MaskVentilation
  , AVG(CASE WHEN label = 'Non-Invasive Blood Pressure Alarm - High' THEN valuenum ELSE null END) as bloodpresureH
  , AVG(CASE WHEN label = 'Non-Invasive Blood Pressure Alarm - Low' THEN valuenum ELSE null END) as bloodpresureL
  , AVG(CASE WHEN label = 'Temperature Celsius' THEN valuenum ELSE null END) as TempCel

  , AVG(CASE WHEN label = 'CVP' THEN valuenum ELSE null END) as CVP
  , AVG(CASE WHEN label = 'Heart rate Alarm - High' THEN valuenum ELSE null END) as HR_High
  , AVG(CASE WHEN label = 'Lowest Heart Rate' THEN valuenum ELSE null END) as Low_HR
  , AVG(CASE WHEN label = 'Heart Rate Alarm - Low' THEN valuenum ELSE null END) as HR_Low
  , AVG(CASE WHEN label = 'RR' THEN valuenum ELSE null END) as RR

  , AVG(CASE WHEN label = 'Arterial Blood Pressure mean' THEN valuenum ELSE null END) as mABP
  , AVG(CASE WHEN label = 'MAP' THEN valuenum ELSE null END) as MAP
  , AVG(CASE WHEN label = 'Arterial Pressure' THEN valuenum ELSE null END) as AP
  



FROM
( -- begin query that extracts the data
  SELECT ie.subject_id, ie.hadm_id, ie.icustay_id
  -- here we assign labels to ITEMIDs
  -- this also fuses together multiple ITEMIDs containing the same data
  , CASE
        WHEN itemid IN (225303) THEN 'Mask Ventilation (Intubation)'
        WHEN itemid IN (223751) THEN 'Non-Invasive Blood Pressure Alarm - High'
        WHEN itemid IN (223752) THEN 'Non-Invasive Blood Pressure Alarm - Low'
        WHEN itemid IN (223761) THEN 'Temperature Celsius'
        
        WHEN itemid IN (220074) THEN 'CVP'
        WHEN itemid IN (220046) THEN 'Heart rate Alarm - High'
        WHEN itemid IN (3494) THEN 'Lowest Heart Rate'
        WHEN itemid IN (220047) THEN 'Heart Rate Alarm - Low'
        WHEN itemid IN (7884) THEN 'RR'
        
        WHEN itemid IN (220052) THEN 'Arterial Blood Pressure mean'
        WHEN itemid IN (438) THEN 'MAP'
        WHEN itemid IN (53) THEN 'Arterial Pressure'
        
      

      ELSE null
    END AS label
  , -- add in some sanity checks on the values
  -- the where clause below requires all valuenum to be > 0, so these are only upper limit checks
    /*
    CASE
      WHEN itemid = 50862 and valuenum >    10 THEN null -- g/dL 'ALBUMIN'
      WHEN itemid = 50868 and valuenum > 10000 THEN null -- mEq/L 'ANION GAP'
      WHEN itemid = 51144 and valuenum <     0 THEN null -- immature band forms, %

    ELSE le.valuenum
    END AS valuenum
    */
    le.valuenum AS valuenum

  FROM z_hyperna_full_patients ie

  LEFT JOIN chartevents le
    ON le.subject_id = ie.subject_id AND le.hadm_id = ie.hadm_id
    AND le.charttime BETWEEN (ie.charttime_first ) AND (ie.charttime_na_high)
    AND le.itemid in
    (
      -- comment is: LABEL | CATEGORY | FLUID | NUMBER OF ROWS IN LABEVENTS
      -- sheet2 2019-11-13 19:04
      225303, --  'Mask'
      223752, -- THEN 'blood'
      223751, -- 'bloodl'
      223761, -- 'Tem'
      -- 223762, -- THEN 'Cel'
      
      220074, --THEN 'CVP'
      220046, --THEN 'HRH'
      3494, --THEN 'LHR'
      220047, --THEN 'HRL'
      7884, --THEN 'RR'
      
      220052, --THEN 'ABP'
      438, --THEN 'MAP'
      53 --THEN 'AP'
     
    )
    AND valuenum IS NOT null AND valuenum > 0 -- lab values cannot be 0 and cannot be negative
) pvt
GROUP BY pvt.subject_id, pvt.hadm_id, pvt.icustay_id
ORDER BY pvt.subject_id, pvt.hadm_id, pvt.icustay_id;
