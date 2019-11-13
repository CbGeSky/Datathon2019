-- This query pivots lab values 
-- labevents between charttime_first and charttime_na_high
-- CREATE materialized VIEW labsfirstday AS
SELECT
  pvt.subject_id, pvt.hadm_id, pvt.icustay_id

  , AVG(CASE WHEN label = 'BNP' THEN valuenum ELSE null END) as BNP
  , AVG(CASE WHEN label = 'Uric Acid' THEN valuenum ELSE null END) as UricAcid
  , AVG(CASE WHEN label = 'Neutrophils' THEN valuenum ELSE null END) as Neutrophils
  , AVG(CASE WHEN label = 'CO2' THEN valuenum ELSE null END) as CO2
  , AVG(CASE WHEN label = 'pO2' THEN valuenum ELSE null END) as pO2

  , AVG(CASE WHEN label = 'Urea Nitrogen' THEN valuenum ELSE null END) as UreaNitrogen
  , AVG(CASE WHEN label = 'Bilirubin' THEN valuenum ELSE null END) as Bilirubin
  , AVG(CASE WHEN label = 'protein' THEN valuenum ELSE null END) as protein
  , AVG(CASE WHEN label = 'phosphate' THEN valuenum ELSE null END) as phosphate
  , AVG(CASE WHEN label = 'chloride' THEN valuenum ELSE null END) as chloride

  , AVG(CASE WHEN label = 'hematocrit' THEN valuenum ELSE null END) as hematocrit
  , AVG(CASE WHEN label = 'creatinine' THEN valuenum ELSE null END) as creatinine
  , AVG(CASE WHEN label = 'troponin T' THEN valuenum ELSE null END) as troponin_T
  , AVG(CASE WHEN label = 'glucose' THEN valuenum ELSE null END) as glucose
  , AVG(CASE WHEN label = 'platelet count' THEN valuenum ELSE null END) as platelet_count

  , AVG(CASE WHEN label = 'D-Dimer' THEN valuenum ELSE null END) as D_Dimer
  , AVG(CASE WHEN label = 'albumin' THEN valuenum ELSE null END) as albumin
  , AVG(CASE WHEN label = 'Calcium' THEN valuenum ELSE null END) as Calcium
  , AVG(CASE WHEN label = 'Sodium' THEN valuenum ELSE null END) as Sodium
  , AVG(CASE WHEN label = 'Potassium' THEN valuenum ELSE null END) as Potassium
  , AVG(CASE WHEN label = 'Magnesium' THEN valuenum ELSE null END) as Magnesium
  --sheet5
  , AVG(CASE WHEN label = 'RR' THEN valuenum ELSE null END) as RR
  , AVG(CASE WHEN label = 'Resp Rate' THEN valuenum ELSE null END) as RespRate
  , AVG(CASE WHEN label = 'NBP-HIGH' THEN valuenum ELSE null END) as NBP_HIGH
  , AVG(CASE WHEN label = 'NBP-LOW' THEN valuenum ELSE null END) as NBP_LOW
  , AVG(CASE WHEN label = 'Temperature' THEN valuenum ELSE null END) as Temperature


FROM
( -- begin query that extracts the data
  SELECT ie.subject_id, ie.hadm_id, ie.icustay_id
  -- here we assign labels to ITEMIDs
  -- this also fuses together multiple ITEMIDs containing the same data
  , CASE
        WHEN itemid IN (227446,225622,7294,50963) THEN 'BNP'
        WHEN itemid IN (225695,853,6058,1541,51007) THEN 'Uric Acid'
        WHEN itemid IN (51256,51349,51232) THEN 'Neutrophils'
        WHEN itemid IN (50818,3808,3810,50804) THEN 'CO2'
        WHEN itemid IN (50821,50817) THEN 'pO2'
        WHEN itemid IN (51006) THEN 'Urea Nitrogen'
        WHEN itemid IN (50885) THEN 'Bilirubin'
        WHEN itemid IN (50976) THEN 'protein'
        WHEN itemid IN (50970) THEN 'phosphate'
        WHEN itemid IN (50902) THEN 'chloride'
        WHEN itemid IN (51221) THEN 'hematocrit'
        WHEN itemid IN (50912) THEN 'creatinine'
        WHEN itemid IN (51003) THEN 'troponin T'
        WHEN itemid IN (50931) THEN 'glucose'
        WHEN itemid IN (51265) THEN 'platelet count'
        WHEN itemid IN (50915) THEN 'D-Dimer'
        WHEN itemid IN (50862) THEN 'albumin'
        WHEN itemid IN (50893,50808) THEN 'Calcium'
        WHEN itemid IN (50824,50983) THEN 'Sodium'
        WHEN itemid IN (50971,50822) THEN 'Potassium'
        WHEN itemid IN (50960) THEN 'Magnesium'
        --sheet5
        WHEN itemid IN (6106,6749) THEN 'RR'
        WHEN itemid IN (224688,224689,224690,619) THEN 'Resp Rate'
        -- WHEN itemid IN SELECT itemid 
        WHEN itemid IN (223751) THEN 'NBP-HIGH'
        WHEN itemid IN (223752) THEN 'NBP-LOW'
        WHEN itemid IN (223762) THEN 'Temperature'

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

  LEFT JOIN labevents le
    ON le.subject_id = ie.subject_id AND le.hadm_id = ie.hadm_id
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
) pvt
GROUP BY pvt.subject_id, pvt.hadm_id, pvt.icustay_id
ORDER BY pvt.subject_id, pvt.hadm_id, pvt.icustay_id;
