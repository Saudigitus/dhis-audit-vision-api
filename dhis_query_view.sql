WITH latest AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY uid ORDER BY createdat DESC) AS rn
    FROM audit
    WHERE createdat >= TO_TIMESTAMP('${since_datetime}', 'YYYY-MM-DD HH24:MI:SS') - INTERVAL '${offset_hours} hours'
)
SELECT *
FROM latest
WHERE rn = 1
ORDER BY createdat DESC
