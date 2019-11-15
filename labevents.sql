-- This query pivots lab values taken in the first 24 hours of a patient's stay

-- Have already confirmed that the unit of measurement is always the same: null or the correct unit

-- DROP MATERIALIZED VIEW IF EXISTS labsfirstday CASCADE;
-- CREATE materialized VIEW labsfirstday AS
SELECT
  pvt.subject_id, pvt.hadm_id, pvt.icustay_id

  , AVG(CASE WHEN label = 'BNP' THEN valuenum ELSE null END) as BNP
  , AVG(CASE WHEN label = 'Urine volume' THEN valuenum ELSE null END) as Urinevolume
  , AVG(CASE WHEN label = 'Specific Gravity' THEN valuenum ELSE null END) as SpecificGravity
  , AVG(CASE WHEN label = 'Potassium Urine' THEN valuenum ELSE null END) as UrinePotassium
  , AVG(CASE WHEN label = 'Hematocrit' THEN valuenum ELSE null END) as hct

  , AVG(CASE WHEN label = 'Hemoglobin' THEN valuenum ELSE null END) as hb
  , AVG(CASE WHEN label = 'Red Blood Cells' THEN valuenum ELSE null END) as brbc
  , AVG(CASE WHEN label = 'Blood Potassium' THEN valuenum ELSE null END) as BloodPotassium
  , AVG(CASE WHEN label = 'Creatinine' THEN valuenum ELSE null END) as creatinine
  , AVG(CASE WHEN label = 'Platete count' THEN valuenum ELSE null END) as Platetecount

  , AVG(CASE WHEN label = 'Neutrophil' THEN valuenum ELSE null END) as Neutrophil
  , AVG(CASE WHEN label = 'Aspartate aminotransferase' THEN valuenum ELSE null END) as Aspartateaminotransferase
  , AVG(CASE WHEN label = 'Monocyte' THEN valuenum ELSE null END) as Monocyte
  , AVG(CASE WHEN label = 'Eosinophil' THEN valuenum ELSE null END) as Eosinophil
  , AVG(CASE WHEN label = 'Basophils' THEN valuenum ELSE null END) as Basophils

  , AVG(CASE WHEN label = 'Lymphocyte' THEN valuenum ELSE null END) as Lymphocyte
  , AVG(CASE WHEN label = 'Osmotic Fragility' THEN valuenum ELSE null END) as OsmoticFragility
  , AVG(CASE WHEN label = 'INR' THEN valuenum ELSE null END) as INR
  , AVG(CASE WHEN label = 'PT' THEN valuenum ELSE null END) as PT
  , AVG(CASE WHEN label = 'PTT' THEN valuenum ELSE null END) as PTT
 
  , AVG(CASE WHEN label = 'Cortisol' THEN valuenum ELSE null END) as Cortisol
  , AVG(CASE WHEN label = 'Bilirubin' THEN valuenum ELSE null END) as Bilirubin
  , AVG(CASE WHEN label = 'Blood gas pH' THEN valuenum ELSE null END) as BloodgaspH
  , AVG(CASE WHEN label = 'HCO3' THEN valuenum ELSE null END) as HCO3
  , AVG(CASE WHEN label = 'O2 saturation' THEN valuenum ELSE null END) as O2saturation

  , AVG(CASE WHEN label = 'pCO2' THEN valuenum ELSE null END) as pCO2
  , AVG(CASE WHEN label = 'blood gas O2' THEN valuenum ELSE null END) as bloodgasO2
  , AVG(CASE WHEN label = 'Blood CO2' THEN valuenum ELSE null END) as BloodCO2
  , AVG(CASE WHEN label = 'Urea Nitrogen' THEN valuenum ELSE null END) as UreaNitrogen
  , AVG(CASE WHEN label = 'Hematocrit' THEN valuenum ELSE null END) as Hematocrit

  , AVG(CASE WHEN label = 'Blood Uric Acid' THEN valuenum ELSE null END) as BloodUricAcid
  , AVG(CASE WHEN label = 'Urine Uric Acid' THEN valuenum ELSE null END) as UrineUricAcid
  , AVG(CASE WHEN label = 'Urine Urea Nitrogen' THEN valuenum ELSE null END) as UrineUreaNitrogen
  , AVG(CASE WHEN label = 'Blood Potassium' THEN valuenum ELSE null END) as BloodPotassium
  , AVG(CASE WHEN label = 'Urine Potassium' THEN valuenum ELSE null END) as UrinePotassium

  , AVG(CASE WHEN label = 'Blood Magnesium' THEN valuenum ELSE null END) as BloodMagnesium
  , AVG(CASE WHEN label = 'Urine Magnesium' THEN valuenum ELSE null END) as UrineMagnesium
  , AVG(CASE WHEN label = 'Blood Calcium' THEN valuenum ELSE null END) as BloodCalcium
  , AVG(CASE WHEN label = 'Urine Calcium' THEN valuenum ELSE null END) as UrineCalcium
  , AVG(CASE WHEN label = 'Glucose' THEN valuenum ELSE null END) as Glucose

  , AVG(CASE WHEN label = 'Urine Glucose' THEN valuenum ELSE null END) as UrineGlucose
  , AVG(CASE WHEN label = 'Blood Osmolatity' THEN valuenum ELSE null END) as BloodOsmolatity
  , AVG(CASE WHEN label = 'Urine Osmolatity' THEN valuenum ELSE null END) as UrineOsmolatity
  , AVG(CASE WHEN label = 'Blood Chloride' THEN valuenum ELSE null END) as BloodChloride
  , AVG(CASE WHEN label = 'Urine Chloride' THEN valuenum ELSE null END) as UrineChloride

  , AVG(CASE WHEN label = 'Blood Albumin' THEN valuenum ELSE null END) as BloodAlbumin
  , AVG(CASE WHEN label = 'Urine Albumin' THEN valuenum ELSE null END) as UrineAlbumin
  , AVG(CASE WHEN label = 'Blood Protein' THEN valuenum ELSE null END) as BloodProtein
  , AVG(CASE WHEN label = 'urine sodium' THEN valuenum ELSE null END) as urinesodium
  , min(CASE WHEN label = 'WBC' THEN valuenum ELSE null end) as WBC_min
  , max(CASE WHEN label = 'WBC' THEN valuenum ELSE null end) as WBC_max
FROM
( -- begin query that extracts the data
  SELECT ie.subject_id, ie.hadm_id, ie.icustay_id
  -- here we assign labels to ITEMIDs
  -- this also fuses together multiple ITEMIDs containing the same data
  , CASE
       
 WHEN itemid IN (227446,225622,7294,50963) THEN 'BNP'
        WHEN itemid IN (51108,51109) THEN 'Urine volume'
        WHEN itemid IN (51498) THEN 'Specific Gravity'
        WHEN itemid IN (51097) THEN 'Potassium Urine'
        WHEN itemid IN (50810,51221) THEN 'Hematocrit'

        WHEN itemid IN (50811,51222,51223,51223,51224,51225,51226,51227) THEN 'Hemoglobin'
        WHEN itemid IN (51279) THEN 'Red Blood Cells'
        WHEN itemid IN (50822,50971) THEN 'Blood Potassium'
        WHEN itemid IN (50912) THEN 'Creatinine'
        WHEN itemid IN (51265) THEN 'Platete count'

        WHEN itemid IN (51256) THEN 'Neutrophil'
        WHEN itemid IN (50878) THEN 'Aspartate aminotransferase'
        WHEN itemid IN (51253,51254) THEN 'Monocyte'
        WHEN itemid IN (51199,51200) THEN 'Eosinophil'
        WHEN itemid IN (51146) THEN 'Basophils'

        WHEN itemid IN (51244,51245) THEN 'Lymphocyte'
        WHEN itemid IN (51258) THEN 'Osmotic Fragility'
        WHEN itemid IN (51237) THEN 'INR'
        WHEN itemid IN (51274) THEN 'PT'
        WHEN itemid IN (51275) THEN 'PTT'
         
        WHEN itemid IN (40909) THEN 'Cortisol'
        WHEN itemid IN (50883,50884,50885) THEN 'Bilirubin'
        WHEN itemid IN (1126,4202,4753,4755,780,3839) THEN 'Blood gas pH'
        WHEN itemid IN (812) THEN 'HCO3'
        WHEN itemid IN (823) THEN 'O2 saturation'

        WHEN itemid IN (50818) THEN 'pCO2'
        WHEN itemid IN (50821) THEN 'blood gas O2'
        WHEN itemid IN (3808) THEN 'Blood CO2'
        WHEN itemid IN (51006) THEN 'Urea Nitrogen'
        WHEN itemid IN (50810,51221) THEN 'Hematocrit'

        
        WHEN itemid IN (51007) THEN 'Blood Uric Acid'
        WHEN itemid IN (51005) THEN 'Urine Uric Acid'
        WHEN itemid IN (51104) THEN 'Urine Urea Nitrogen'
        WHEN itemid IN (50971,50822) THEN 'Blood Potassium'
        WHEN itemid IN (51097) THEN 'Urine Potassium'

        WHEN itemid IN (50960) THEN 'Blood Magnesium'
        WHEN itemid IN (51088) THEN 'Urine Magnesium'
        WHEN itemid IN (50808,50893) THEN 'Blood Calcium'
        WHEN itemid IN (51077) THEN 'Urine Calcium'
        WHEN itemid IN (50931,50809) THEN 'Glucose'

        WHEN itemid IN (51084) THEN 'Urine Glucose'
        WHEN itemid IN (50964) THEN 'Blood Osmolatity'
        WHEN itemid IN (51093) THEN 'Urine Osmolatity'
        WHEN itemid IN (50806,50902) THEN 'Blood Chloride'
        WHEN itemid IN (51078) THEN 'Urine Chloride'

        WHEN itemid IN (50862) THEN 'Blood Albumin'
        WHEN itemid IN (51069) THEN 'Blood Osmolatity'
        WHEN itemid IN (50976) THEN 'Blood Protein'
        WHEN itemid IN (51100) THEN 'urine sodium'
        WHEN itemid = 51300 THEN 'WBC'
        WHEN itemid = 51301 THEN 'WBC'
 

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
    -- AND le.charttime BETWEEN (ie.charttime_first ) AND (ie.charttime_na_high) --forward
    AND le.charttime BETWEEN (ie.charttime_na_high ) AND (ie.charttime_last) --backward
    AND le.ITEMID in
    (
      -- comment is: LABEL | CATEGORY | FLUID | NUMBER OF ROWS IN LABEVENTS
      -- sheet2 2019-11-13 19:04
        227446,225622,7294,50963,
        51108,51109,
        51498,
        51097,
        50810,51221,
        50811,51222,51223,51223,51224,51225,51226,51227,
        51279,
        50822,50971,
        50912,
        51265,
        51256,
        50878,
        51253,51254,
        51199,51200,
        51146,
        51244,51245,
        51258,
        51237,
        51274,
        51275,
        40909,
        50883,50884,50885,
        1126,4202,4753,4755,780,3839,
        812,
        823,
        50818,
        50821,
        3808,
        51006,
        50810,51221,
        
        51007,
        51005,
        51104,
        50971,50822,
        51097,
        50960,
        51088,
        50808,50893,
        51077,
        50931,50809,
        51084,
        50964,
        51093,
        50806,50902,
        51078,
        50862,
        51069,
        50976,
        51100,
        51300 ,
        51301
    )
    AND valuenum IS NOT null AND valuenum > 0 -- lab values cannot be 0 and cannot be negative
) pvt
GROUP BY pvt.subject_id, pvt.hadm_id, pvt.icustay_id
ORDER BY pvt.subject_id, pvt.hadm_id, pvt.icustay_id;
