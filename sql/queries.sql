-- =============================================================================
-- Analytical SQL Queries for A/B Test Analysis
-- Demonstrates: CTEs, window functions (LAG, running totals), date functions,
-- CASE expressions, subqueries
-- =============================================================================

-- 1. Daily conversion funnel by group
SELECT
    DATE(timestamp) AS test_date,
    "group",
    COUNT(*) AS visitors,
    SUM(converted) AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate
FROM ab_results
GROUP BY DATE(timestamp), "group"
ORDER BY test_date, "group";


-- 2. Country performance with traffic share (window function)
SELECT
    country,
    "group",
    COUNT(*) AS visitors,
    SUM(converted) AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY country), 2)
        AS pct_of_country_traffic
FROM ab_results
GROUP BY country, "group"
ORDER BY country, "group";


-- 3. Hourly conversion pattern with LAG window function
WITH hourly AS (
    SELECT
        CAST(SUBSTR(timestamp, 12, 2) AS INTEGER) AS hour_of_day,
        "group",
        COUNT(*) AS visitors,
        SUM(converted) AS conversions
    FROM ab_results
    GROUP BY hour_of_day, "group"
)
SELECT
    hour_of_day,
    "group",
    visitors,
    conversions,
    ROUND(100.0 * conversions / visitors, 2) AS conversion_rate,
    LAG(ROUND(100.0 * conversions / visitors, 2))
        OVER (PARTITION BY "group" ORDER BY hour_of_day) AS prev_hour_rate
FROM hourly
ORDER BY hour_of_day, "group";


-- 4. Cumulative conversion with running totals (window function)
WITH daily AS (
    SELECT
        DATE(timestamp) AS test_date,
        "group",
        SUM(converted) AS daily_conversions,
        COUNT(*) AS daily_visitors
    FROM ab_results
    GROUP BY DATE(timestamp), "group"
)
SELECT
    test_date,
    "group",
    daily_conversions,
    SUM(daily_conversions) OVER (
        PARTITION BY "group" ORDER BY test_date
    ) AS cumulative_conversions,
    SUM(daily_visitors) OVER (
        PARTITION BY "group" ORDER BY test_date
    ) AS cumulative_visitors,
    ROUND(100.0 * SUM(daily_conversions) OVER (
        PARTITION BY "group" ORDER BY test_date
    ) / SUM(daily_visitors) OVER (
        PARTITION BY "group" ORDER BY test_date
    ), 3) AS running_conversion_rate
FROM daily
ORDER BY test_date, "group";


-- 5. Day-of-week analysis with CASE + STRFTIME
WITH dow AS (
    SELECT
        CASE CAST(STRFTIME('%w', timestamp) AS INTEGER)
            WHEN 0 THEN 'Sunday'
            WHEN 1 THEN 'Monday'
            WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday'
            WHEN 4 THEN 'Thursday'
            WHEN 5 THEN 'Friday'
            WHEN 6 THEN 'Saturday'
        END AS day_name,
        CAST(STRFTIME('%w', timestamp) AS INTEGER) AS day_num,
        "group",
        converted
    FROM ab_results
)
SELECT
    day_name,
    "group",
    COUNT(*) AS visitors,
    SUM(converted) AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate
FROM dow
GROUP BY day_name, day_num, "group"
ORDER BY day_num, "group";
