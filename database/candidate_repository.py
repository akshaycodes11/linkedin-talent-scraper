"""
database/candidate_repository.py

Handles all database operations related to candidates.
"""

import json
from psycopg2.extras import execute_values, Json
from database.connection import get_connection


class CandidateRepository:

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    # ---------------------------------------------------------
    # Create Table
    # ---------------------------------------------------------

    def create_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS candidates (

            id SERIAL PRIMARY KEY,

            linkedin_url TEXT UNIQUE NOT NULL,

            full_name TEXT,

            headline TEXT,

            current_company TEXT,

            location TEXT,

            total_experience_years INTEGER,

            skills TEXT[],

            search_query TEXT,

            source TEXT,

            raw_text TEXT,

            raw_json JSONB,

            created_at TIMESTAMP DEFAULT NOW()

        );
        """

        self.cursor.execute(query)
        self.conn.commit()

    # ---------------------------------------------------------
    # Insert One Candidate
    # ---------------------------------------------------------

    def insert_candidates(self, candidates):

        if not candidates:
            return {
                "inserted": 0,
                "duplicates": 0
            }

        query = """
        INSERT INTO candidates (

            linkedin_url,
            full_name,
            headline,
            current_company,
            location,
            total_experience_years,
            skills,
            search_query,
            source,
            raw_text,
            raw_json

        )

        VALUES %s

        ON CONFLICT (linkedin_url)
        DO NOTHING

        RETURNING id;
        """

        values = [

            (

                candidate["linkedin_url"],
                candidate["full_name"],
                candidate["headline"],
                candidate["current_company"],
                candidate["location"],
                candidate["total_experience_years"],
                candidate["skills"],
                candidate["search_query"],
                candidate["source"],
                candidate["raw_text"],
                Json(candidate["raw_json"])

            )

            for candidate in candidates

        ]

        execute_values(
            self.cursor,
            query,
            values
        )

        inserted = len(self.cursor.fetchall())

        self.conn.commit()

        return {

            "inserted": inserted,

            "duplicates": len(candidates) - inserted

        }

    # # ---------------------------------------------------------
    # # Bulk Insert
    # # ---------------------------------------------------------

    # def insert_candidates(self, candidates):

    #     if not candidates:
    #         return

    #     query = """
    #     INSERT INTO candidates (

    #         linkedin_url,
    #         full_name,
    #         headline,
    #         current_company,
    #         location,
    #         total_experience_years,
    #         skills,
    #         search_query,
    #         source,
    #         raw_text,
    #         raw_json

    #     )

    #     VALUES (

    #         %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s

    #     )

    #     ON CONFLICT (linkedin_url)
    #     DO NOTHING;
    #     """

    #     values = []

    #     for candidate in candidates:

    #         values.append(

    #             (
    #                 candidate["linkedin_url"],
    #                 candidate["full_name"],
    #                 candidate["headline"],
    #                 candidate["current_company"],
    #                 candidate["location"],
    #                 candidate["total_experience_years"],
    #                 candidate["skills"],
    #                 candidate["search_query"],
    #                 candidate["source"],
    #                 candidate["raw_text"],
    #                 Json(candidate["raw_json"])
    #             )

    #         )

    #     self.cursor.executemany(query, values)

    #     self.conn.commit()
    # ---------------------------------------------------------
    # Count Candidates
    # ---------------------------------------------------------

    def count_candidates(self):

        self.cursor.execute(

            "SELECT COUNT(*) AS total FROM candidates"

        )

        result = self.cursor.fetchone()

        return result["total"]

    # ---------------------------------------------------------
    # Get All Candidates
    # ---------------------------------------------------------

    def get_all_candidates(self):

        self.cursor.execute(

            """
            SELECT *
            FROM candidates
            ORDER BY created_at DESC
            """
        )

        return self.cursor.fetchall()

    # ---------------------------------------------------------
    # Candidate Exists
    # ---------------------------------------------------------

    def candidate_exists(self, linkedin_url):

        self.cursor.execute(

            """
            SELECT 1
            FROM candidates
            WHERE linkedin_url=%s
            """,

            (linkedin_url,)

        )

        return self.cursor.fetchone() is not None

    # ---------------------------------------------------------
    # Close Connection
    # ---------------------------------------------------------

    def close(self):

        self.cursor.close()
        self.conn.close()
        