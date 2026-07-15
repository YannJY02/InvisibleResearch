# This script sets up the database used by the acquisition capability.
set -e

: "${DATA_ROOT:?Set DATA_ROOT to the external InvisibleResearch data directory}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$PROJECT_ROOT"

# Create a virtual environment.
python3 -m venv venv
source venv/bin/activate

# Install the required packages.
pip install "modin[ray]" sqlalchemy


# Install the database driver.
gzip -dc "$DATA_ROOT/raw/database.sql.gz" > "$DATA_ROOT/dump.sql"

# using docker move the database to a large disk
docker run -d \
  --name PKPresearch-db \
  -v "$DATA_ROOT/mysql_data:/var/lib/mysql" \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=secret \
  mysql:latest

# check if the docker is running
docker ps

# pipeline import the database
docker exec -i PKPresearch-db mysql -uroot -psecret -e "CREATE DATABASE IF NOT EXISTS invisible_research;"
docker exec -i PKPresearch-db mysql -uroot -psecret invisible_research < "$DATA_ROOT/dump.sql"

# Run the Python script to read from the database
export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
python -m invisible_research.acquisition.database_sample
