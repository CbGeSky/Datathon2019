/*
入icu48h发生高钠血症患者提取修正
--加入了确定为高钠血的钠数值
--解决思路如下，但是有点过于麻烦了
-- http://www.voidcn.com/article/p-vleioxic-bsk.html
-- group by 聚合函数问题解决，需要加一次自身连接
*/
--CREATE TABLE z_high_na_all AS
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

/*生化指标提取的一个思路 11-13 00:19
mimic项目中有个labs-first-day.sql,
把其中用来确定病人的icustays表替换成高钠id的表，
就可以完美融合(注意高钠id表的变量不要重名)

然后就是非聚合变量放不进去的问题(na的值)，
这个再对自身(高钠id表)做一次连接写进去即可
*/