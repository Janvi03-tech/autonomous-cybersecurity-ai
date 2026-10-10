import os
import shutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_FILE = BASE_DIR / "sql" / "schema.sql"
PSQL_EXE = shutil.which("psql") or r"C:\Program Files\PostgreSQL\14\bin\psql.exe"

load_dotenv(BASE_DIR / ".env", override=True)


def main():
    required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing = [key for key in required if not os.environ.get(key)]

    if missing:
        raise RuntimeError(
            "Missing database configuration: " + ", ".join(missing)
        )

    if not SCHEMA_FILE.is_file():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")

    if not Path(PSQL_EXE).is_file() and not shutil.which(PSQL_EXE):
        raise FileNotFoundError(
            "Could not find psql. Install PostgreSQL client tools or update PSQL_EXE."
        )

    env = os.environ.copy()
    env["PGPASSWORD"] = os.environ["DB_PASSWORD"]

    command = [
        PSQL_EXE,
        "-v", "ON_ERROR_STOP=1",
        "-h", os.environ["DB_HOST"],
        "-p", os.environ["DB_PORT"],
        "-U", os.environ["DB_USER"],
        "-d", os.environ["DB_NAME"],
        "-f", str(SCHEMA_FILE),
    ]

    subprocess.run(command, env=env, check=True)
    print("Database schema initialized successfully.")


if __name__ == "__main__":
    main()
