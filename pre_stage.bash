#  This script is used to set up the environment for the InvisibleResearch project.
cd ~/projects
git clone https://github.com/YannJY02/InvisibleResearch.git
cd InvisibleResearch

# Create a virtual environment.
python3 -m venv venv
source venv/bin/activate

# Install the required packages.
pip install "modin[ray]" sqlalchemy


# Install the database driver.
gzip -dc database.sql.gz > dump.sql

# using docker move the database to a large disk
docker run -d \
  --name PKPresearch-db \
  -v /Volumes/Seagate/Research/InvisibleResearch/mysql_data:/var/lib/mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=secret \
  mysql:latest

# check if the docker is running
docker ps

# pipeline import the database
docker exec -i PKPresearch-db mysql -uroot -psecret -e "CREATE DATABASE IF NOT EXISTS invisible_research;"
cat /Volumes/Seagate/Research/InvisibleResearch/dump.sql | docker exec -i PKPresearch-db mysql -uroot -psecret invisible_research

# Run the Python script to read from the database
python read_database.py