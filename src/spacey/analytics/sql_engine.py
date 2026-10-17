"""
SpaceY Intelligence - SQLite Analytical Query and Reporting Engine
Creates analytical tables, views, and reproducible metrics with exact sample counts and denominators.
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

from spacey.config import SQLITE_DB_PATH
from spacey.logging_config import setup_logger

logger = setup_logger("spacey.sql_engine")


class SpaceYAnalyticsDB:
    """Manages SQLite analytical database, tables, and dimensional views."""

    def __init__(self, db_path: Path = SQLITE_DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def initialize_database(self, df: pd.DataFrame) -> None:
        """
        Loads flight archive into SQLite and creates analytical views.
        Guarantees that every ratio includes denominators and sample sizes.
        """
        logger.info("Initializing SQLite database at %s with %d records", self.db_path, len(df))
        with self.get_connection() as conn:
            # Write main table
            df.to_sql("launches", conn, if_exists="replace", index=False)

            cursor = conn.cursor()

            # View 1: Overall Summary
            cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_overall_summary AS
            SELECT
                COUNT(*) AS total_launches,
                SUM(Class) AS total_successful_landings,
                COUNT(*) - SUM(Class) AS total_failed_or_unattempted,
                ROUND(AVG(Class) * 100.0, 2) AS overall_success_rate_pct,
                MIN(Year) AS earliest_year,
                MAX(Year) AS latest_year,
                ROUND(AVG(PayloadMass), 1) AS avg_payload_mass_kg
            FROM launches;
            """)

            # View 2: Site Analytics (with sample counts & denominators)
            cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_site_analytics AS
            SELECT
                LaunchSite,
                COUNT(*) AS total_launches,
                SUM(Class) AS successful_landings,
                COUNT(*) - SUM(Class) AS failed_or_unattempted,
                ROUND(AVG(Class) * 100.0, 2) AS success_rate_pct,
                ROUND(AVG(PayloadMass), 1) AS avg_payload_kg,
                ROUND(MIN(PayloadMass), 1) AS min_payload_kg,
                ROUND(MAX(PayloadMass), 1) AS max_payload_kg
            FROM launches
            GROUP BY LaunchSite
            ORDER BY total_launches DESC;
            """)

            # View 3: Orbit Analytics
            cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_orbit_analytics AS
            SELECT
                Orbit,
                COUNT(*) AS total_launches,
                SUM(Class) AS successful_landings,
                COUNT(*) - SUM(Class) AS failed_or_unattempted,
                ROUND(AVG(Class) * 100.0, 2) AS success_rate_pct,
                ROUND(AVG(PayloadMass), 1) AS avg_payload_kg
            FROM launches
            GROUP BY Orbit
            ORDER BY total_launches DESC;
            """)

            # View 4: Annual Trends
            cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_annual_trends AS
            SELECT
                Year,
                COUNT(*) AS total_launches,
                SUM(Class) AS successful_landings,
                COUNT(*) - SUM(Class) AS failed_or_unattempted,
                ROUND(AVG(Class) * 100.0, 2) AS success_rate_pct,
                ROUND(AVG(PayloadMass), 1) AS avg_payload_kg
            FROM launches
            WHERE Year IS NOT NULL
            GROUP BY Year
            ORDER BY Year ASC;
            """)

            # View 5: Payload Mass Bands
            cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_payload_bands AS
            SELECT
                CASE
                    WHEN PayloadMass < 3000 THEN 'Light (<3,000 kg)'
                    WHEN PayloadMass BETWEEN 3000 AND 6000 THEN 'Medium (3,000-6,000 kg)'
                    WHEN PayloadMass BETWEEN 6000 AND 10000 THEN 'Heavy (6,000-10,000 kg)'
                    ELSE 'Super Heavy (>10,000 kg)'
                END AS payload_category,
                COUNT(*) AS total_launches,
                SUM(Class) AS successful_landings,
                COUNT(*) - SUM(Class) AS failed_or_unattempted,
                ROUND(AVG(Class) * 100.0, 2) AS success_rate_pct,
                ROUND(AVG(PayloadMass), 1) AS avg_payload_kg
            FROM launches
            GROUP BY payload_category
            ORDER BY total_launches DESC;
            """)

            # View 6: Reusable Booster Analysis
            cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_booster_reuse AS
            SELECT
                CASE WHEN Reused = 1 THEN 'Flight-Proven (Reused)' ELSE 'Maiden Flight' END AS booster_status,
                COUNT(*) AS total_launches,
                SUM(Class) AS successful_landings,
                COUNT(*) - SUM(Class) AS failed_or_unattempted,
                ROUND(AVG(Class) * 100.0, 2) AS success_rate_pct
            FROM launches
            GROUP BY Reused
            ORDER BY total_launches DESC;
            """)

            conn.commit()
            logger.info("Created 6 analytical database views successfully.")

    def run_query(self, query: str) -> pd.DataFrame:
        """Executes a SQL query and returns results as a pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def get_overall_summary(self) -> pd.DataFrame:
        return self.run_query("SELECT * FROM v_overall_summary;")

    def get_site_analytics(self) -> pd.DataFrame:
        return self.run_query("SELECT * FROM v_site_analytics;")

    def get_orbit_analytics(self) -> pd.DataFrame:
        return self.run_query("SELECT * FROM v_orbit_analytics;")

    def get_annual_trends(self) -> pd.DataFrame:
        return self.run_query("SELECT * FROM v_annual_trends;")

    def get_payload_bands(self) -> pd.DataFrame:
        return self.run_query("SELECT * FROM v_payload_bands;")

    def get_booster_reuse_analytics(self) -> pd.DataFrame:
        return self.run_query("SELECT * FROM v_booster_reuse;")
