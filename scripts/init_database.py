import os

from sqlalchemy import create_engine, text

from codenerva.infrastructure.database.schema import create_schema


def main() -> None:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    with engine.connect() as connection:
        database_name = connection.scalar(text("SELECT current_database()"))

        print(f"Connected to PostgreSQL database: {database_name}")

    create_schema(
        engine=engine,
    )

    print("Database schema created successfully.")


if __name__ == "__main__":
    main()
