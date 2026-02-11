-- Core A/B metrics for BI parity checks.
WITH cleaned AS (
    SELECT
        user_id,
        timestamp,
        "group",
        landing_page,
        converted
    FROM ab_data
    WHERE ("group" = 'control' AND landing_page = 'old_page')
       OR ("group" = 'treatment' AND landing_page = 'new_page')
),
latest AS (
    SELECT *
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp DESC) AS rn
        FROM cleaned
    ) t
    WHERE rn = 1
)
SELECT
    "group" AS variant,
    COUNT(*) AS observations,
    SUM(converted) AS conversions,
    AVG(converted) AS conversion_rate
FROM latest
GROUP BY 1;
