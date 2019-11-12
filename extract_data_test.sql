-- extract data
-- na in table labitems itemid=50983
SET search_path to mimiciii;
SELECT 
  subject_id,hadm_id,min(charttime) as chartime_new,valuenum
FROM labevents
where itemid = 50983 and valuenum > 145 
GROUP BY subject_id,hadm_id,valuenum limit 100 ;

--查询指定项目
SELECT COUNT(DISTINCT subject_id) FROM chartevents 
WHERE itemid IN (SELECT itemid FROM d_items WHERE CATEGORY ILIKE '%APACHE II%')

--时间精度阶段 date_trunc('day',intime) + interval '2' day https://blog.csdn.net/luckypeng/article/details/48814063

SELECT 
  new.subject_id,new.hadm_id,new.charttime_new,new.valuenum AS input_value,
  lab.charttime,lab.valuenum AS output_values
FROM
(
    SELECT *
    --lab.subject_id,lab.hadm_id,lab.charttime,lab.valuenum
    -- 不允许嵌套调用聚合函数count(min(charttime))
    FROM labevents lab
    WHERE lab.itemid = 50983 AND lab.valuenum > 145 
    -- GROUP BY lab.subject_id,lab.hadm_id,lab.valuenum
) new
LEFT JOIN icustay lab
ON new.subject_id = lab.subject_id AND new.hadm_id=lab.hadm_id 
AND lab.itemid = 50983
AND lab.charttime BETWEEN (new.charttime_new + interval '2' hour) AND (new.charttime_new + interval '1' day)
