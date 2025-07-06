from sqlalchemy import create_engine, text
import os

engine = create_engine(os.getenv("DATABASE_URL"))

def log_event(endpoint: str, status_code: int):
    with engine.begin() as conn:
        
        conn.execute(text("""
            DELETE FROM logs
            WHERE id NOT IN (
                SELECT id FROM logs
                ORDER BY timestamp DESC
                LIMIT 49
            )
        """))

        conn.execute(text("""
            INSERT INTO logs (endpoint, status_code)
            VALUES (:endpoint, :status_code)
        """), {"endpoint": endpoint, "status_code": status_code})