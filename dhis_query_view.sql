WITH latest AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY uid ORDER BY createdat DESC) AS rn
    FROM audit
    WHERE createdat >= TO_TIMESTAMP(${since_epoch}) - make_interval(hours => ${offset_hours})
)
SELECT *
FROM latest
WHERE rn = 1
ORDER BY createdat DESC
