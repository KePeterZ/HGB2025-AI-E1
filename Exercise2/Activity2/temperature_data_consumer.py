import time
from datetime import datetime, timedelta
import psycopg

# -------------------------
# PostgreSQL connection parameters
# -------------------------
DB_NAME = "office_db"
DB_USER = "postgres"
DB_PASSWORD = "postgrespw"
DB_HOST = "localhost"
DB_PORT = 5432

# -------------------------
# Connect to PostgreSQL
# -------------------------
with psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
) as conn:

    with conn.cursor() as cursor:
        print("Connected to PostgreSQL, starting consumer...")

        # -------------------------
        # Periodically compute average over last 10 minutes
        # -------------------------
        try:
            while True:
                ten_minutes_ago = datetime.now() - timedelta(minutes=10)

                # Fetch readings from last 10 minutes
                cursor.execute(
                    """
                    SELECT AVG(temperature) 
                    FROM temperature_readings
                    WHERE recorded_at >= %s
                    """,
                    (ten_minutes_ago,)
                )
                result = cursor.fetchone()
                avg_temp = result[0] if result[0] is not None else None

                if avg_temp is not None:
                    print(f"{datetime.now()} - Average temperature last 10 minutes: {avg_temp:.2f} °C")
                else:
                    print(f"{datetime.now()} - No data in last 10 minutes.")

                time.sleep(600)  # wait 10 minutes

        except KeyboardInterrupt:
            print("Stopped consuming data.")
        finally:
            print("Exiting.")
