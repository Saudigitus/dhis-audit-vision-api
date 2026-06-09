WITH latest AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY uid ORDER BY createdat DESC) AS rn
    FROM audit
    WHERE uid = '${resource_uid}'
      AND createdat >= TO_TIMESTAMP('${created_at}', 'YYYY-MM-DD HH24_MI_SS') - make_interval(hours => ${offset_hours})
)
SELECT *
FROM latest
WHERE rn = 1
ORDER BY createdat DESC
