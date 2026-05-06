
-- Query to get the latest audit records for all resources since a specific datetime, excluding records created by 'system-process'

WITH latest AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY uid ORDER BY createdat DESC) AS rn
    FROM audit
    WHERE createdat >= TO_TIMESTAMP('${since_datetime}', 'YYYY-MM-DD HH24:MI:SS') - INTERVAL '${offset_hours} hours'
)
SELECT *
FROM latest
WHERE rn = 1 and createdby <> 'system-process'
ORDER BY createdat DESC



---------------------------------------------
-- Query to get the latest audit record for a specific resource uid
SELECT *
FROM audit
 WHERE  uid = '${resource_uid}'  and createdby <> 'system-process'
ORDER BY createdat DESC
LIMIT 1
