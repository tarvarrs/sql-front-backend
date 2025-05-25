#!/bin/bash
set -e

# Function to create database and restore from backup if exists
create_db() {
    local db=$1
    echo "Creating database: $db"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE $db;
EOSQL

    # Restore from SQL backup if exists
    if [ -f "/backups/$db.sql" ]; then
        echo "Restoring $db from SQL backup"
        psql -U "$POSTGRES_USER" -d "$db" -f "/backups/$db.sql"
    fi
}

# Create users_db
create_db "users_db"

# Create game_db and set up restricted user
echo "Creating game_db and setting up restricted user"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE game_db;
    
    -- Create restricted user for game_db
    CREATE USER game_readonly WITH PASSWORD '${GAME_DB_PASSWORD}';
    
    -- Connect to game_db
    \c game_db
    
    -- Grant connect permission
    GRANT CONNECT ON DATABASE game_db TO game_readonly;
    
    -- Grant usage on schema
    GRANT USAGE ON SCHEMA public TO game_readonly;
    
    -- Grant SELECT only permissions on all existing tables
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO game_readonly;
    
    -- Grant SELECT permissions on future tables
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO game_readonly;
EOSQL

# Restore game_db if SQL backup exists
if [ -f "/backups/game_db.sql" ]; then
    echo "Restoring game_db from SQL backup"
    psql -U "$POSTGRES_USER" -d "game_db" -f "/backups/game_db.sql"
fi 