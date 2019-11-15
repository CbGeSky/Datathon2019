-- This query pivots lab values-- This query pivots lab values 
-- labevents between charttime_na_high and charttime_last
-- CREATE materialized VIEW labsfirstday AS
SELECT
  forw_in_bolus.subject_id, forw_in_bolus.hadm_id, forw_in_bolus.icustay_id

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

  LEFT JOIN z_colloid_bolus le
    ON le.icustay_id = ie.icustay_id
    AND le.charttime BETWEEN (ie.charttime_first ) AND (ie.charttime_na_high)
) forw_in_bolus
GROUP BY forw_in_bolus.subject_id, forw_in_bolus.hadm_id, forw_in_bolus.icustay_id
ORDER BY forw_in_bolus.subject_id, forw_in_bolus.hadm_id, forw_in_bolus.icustay_id;
