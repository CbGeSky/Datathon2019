SET search_path to mimiciii;

/*
select count(subject_id) FROM
(SELECT 
  lab.subject_id,lab.hadm_id,min(lab.charttime) as chartime_new,lab.valuenum
  -- 不允许嵌套调用聚合函数count(min(charttime))
FROM labevents lab

where lab.itemid = 50983 and lab.valuenum > 149 
GROUP BY lab.subject_id,lab.hadm_id,lab.valuenum) new

-- 50983 >145 min(chartime) subject_id:30030 hadm_id:27711
-- 50983 >149 min(chartime) subject_id:8781 hadm_id:8395
*/


-- 50983 >145 2h to 24h 52159
-- 50983 >149 2h to 24h 19835
SELECT 
  /*
  new.subject_id,new.hadm_id,new.charttime_new,new.valuenum AS input_value,
  lab.charttime,lab.valuenum AS output_values
  */
  (lab.charttime - new.charttime_new) as timegap
FROM
(
    SELECT 
    lab.subject_id,lab.hadm_id,min(lab.charttime) AS charttime_new,lab.valuenum
    -- 不允许嵌套调用聚合函数count(min(charttime))
    FROM labevents lab
    WHERE lab.itemid = 50983 AND lab.valuenum > 145 
    GROUP BY lab.subject_id,lab.hadm_id,lab.valuenum
) new
LEFT JOIN labevents lab
ON new.subject_id = lab.subject_id AND new.hadm_id=lab.hadm_id 
AND lab.itemid = 50983
AND lab.charttime BETWEEN (new.charttime_new + interval '2' hour) AND (new.charttime_new + interval '1' day)
