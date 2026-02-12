"""SQLite database utilities for A/B test analysis.

Demonstrates SQL proficiency: CTEs, window functions, date functions,
aggregations, and subqueries for conversion funnel analysis.
"""

import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "abtest.db")


def create_database(df: pd.DataFrame, db_path: str = None) -> str:
    """Load A/B test data into a SQLite database."""
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    df_copy = df.copy()
    df_copy["timestamp"] = df_copy["timestamp"].astype(str)
    df_copy.to_sql("ab_results", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_group ON ab_results('group')")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_country ON ab_results(country)")
    conn.commit()
    conn.close()
    return db_path


def run_query(query: str, db_path: str = None) -> pd.DataFrame:
    """Execute a SQL query and return results."""
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result


QUERIES = {
    "daily_conversion_funnel": """
        SELECT
            DATE(timestamp) AS test_date,
            "group",
            COUNT(*) AS visitors,
            SUM(converted) AS conversions,
            ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate
        FROM ab_results
        GROUP BY DATE(timestamp), "group"
        ORDER BY test_date, "group"
    """,

    "country_performance": """
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
        ORDER BY country, "group"
    """,

    "hourly_conversion_pattern": """
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
        ORDER BY hour_of_day, "group"
    """,

    "cumulative_conversions": """
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
            daily_visitors,
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
        ORDER BY test_date, "group"
    """,

    "day_of_week_analysis": """
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
        ORDER BY day_num, "group"
    """,
}
