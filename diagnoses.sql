----------------------诊断提取 11月14日
-- 没法一次性搞定，只能是一个一个来了
-- 统计特定疾病
WITH diabetes AS
(
  SELECT na.hadm_id,COUNT(seq_num) AS icd_count FROM diagnoses_icd d
  INNER JOIN z_hyperna_full_patients na
  ON d.subject_id = na.subject_id AND d.hadm_id = na.hadm_id
  AND icd9_code IN (SELECT icd9_code FROM d_icd_diagnoses WHERE LONG_TITLE LIKE '%Diabetes%' AND LONG_TITLE NOT LIKE '%diabetes insipidus%' AND LONG_TITLE NOT LIKE '%pregnancy%'
  AND LONG_TITLE NOT LIKE '%Screening for diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Neonatal diabetes mellitus%' AND LONG_TITLE NOT LIKE '%Family history%' )
  GROUP BY na.hadm_id
)
SELECT 
  na.subject_id, na.hadm_id, na.icustay_id, -- icd_count
  sum(CASE WHEN icd_count IS NOT NULL THEN 1 ELSE 0 END) AS diabetes
FROM z_hyperna_full_patients na
LEFT JOIN diabetes d
ON d.hadm_id = na.hadm_id
GROUP BY na.subject_id, na.hadm_id, na.icustay_id
ORDER BY na.subject_id, na.hadm_id, na.icustay_id;

