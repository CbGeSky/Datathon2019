-- This query pivots lab values-- This query pivots lab values 
-- labevents between charttime_na_high and charttime_last
-- CREATE materialized VIEW labsfirstday AS
SELECT
  forw_in_cv.subject_id, forw_in_cv.hadm_id, forw_in_cv.icustay_id

  , SUM(CASE WHEN label = 'BNP' THEN amount ELSE null END) as BNP
  , SUM(CASE WHEN label = 'Uric Acid' THEN valuenum ELSE null END) as UricAcid
  , AVG(CASE WHEN label = 'Neutrophils' THEN valuenum ELSE null END) as Neutrophils
  , AVG(CASE WHEN label = 'CO2' THEN valuenum ELSE null END) as CO2
  , AVG(CASE WHEN label = 'pO2' THEN valuenum ELSE null END) as pO2

FROM
( -- begin query that extracts the data
  SELECT ie.subject_id, ie.hadm_id, ie.icustay_id
  -- here we assign labels to ITEMIDs
  -- this also fuses together multiple ITEMIDs containing the same data
  , CASE
        WHEN itemid IN (227446,225622,7294,50963) THEN 'BNP'
        
        -- amountuom ml       
        WHEN itemid IN (SELECT itemid FROM inputevents_cv WHERE amountuom = 'ml')
        AND IN () THEN 'itemname/ml'
        /*
        -- amountuom mg
        WHEN itemid IN (SELECT itemid FROM inputevents_cv WHERE amountuom = 'ml'
        AND 
          ) THEN 'itemname/mg'
          */


        WHEN itemid IN (51256,51349,51232) THEN 'Neutrophils'
        WHEN itemid IN (50818,3808,3810,50804) THEN 'CO2'
        WHEN itemid IN (50821,50817) THEN 'pO2'
        WHEN itemid IN (51006) THEN 'Urea Nitrogen'


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
    le.amount AS amount

  FROM z_hyperna_full_patients ie

  LEFT JOIN inputevents_cv le
    ON le.subject_id = ie.subject_id AND le.hadm_id = ie.hadm_id AND le.icustay_id = ie.icustay_id
    AND le.charttime BETWEEN (ie.charttime_first ) AND (ie.charttime_na_high)
    AND le.itemid in
    (
      -- comment is: LABEL | CATEGORY | FLUID | NUMBER OF ROWS IN LABEVENTS
      -- sheet2 2019-11-13 19:04
      227446,225622,7294,50963, --  'BNP'
      225695,853,6058,1541,51007, -- THEN 'Uric Acid'
      51256,51349,51232, -- 'Neutrophils'
      50818,3808,3810,50804, -- 'CO2'
      50821,50817, -- THEN 'pO2'
      51006, --THEN 'Urea Nitrogen'
      50885, --THEN 'Bilirubin'
      50976, --THEN 'protein'
      50970, --THEN 'phosphate'
      50902, --THEN 'chloride'
      51221, --THEN 'hematocrit'
      50912, --THEN 'creatinine'
      51003, --THEN 'troponin T'
      50931, --THEN 'glucose'
      51265, --THEN 'platelet count'
      50915, --THEN 'D-Dimer'
      50862, --THEN 'albumin'
      50893,50808, --THEN 'Calcium'
      50824,50983, -- THEN 'Sodium'
      50971,50822, -- THEN 'Potassium'
      50960, -- THEN 'Magnesium'
      -- sheet5 2019-11-13 19:04
      6106,6749, --  THEN 'RR'
      224688,224689,224690,619, --  THEN 'Resp Rate'
        -- WHEN itemid IN SELECT itemid 
      223751, --  THEN 'NBP-HIGH'
      223752, --  THEN 'NBP-LOW'
      223762 --  THEN 'Temperature'
    )
    AND valuenum IS NOT null AND valuenum > 0 -- lab values cannot be 0 and cannot be negative
) forw_in_cv
GROUP BY forw_in_cv.subject_id, forw_in_cv.hadm_id, forw_in_cv.icustay_id
ORDER BY forw_in_cv.subject_id, forw_in_cv.hadm_id, forw_in_cv.icustay_id;
