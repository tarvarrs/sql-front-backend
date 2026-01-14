#!/bin/bash
set -e

create_db_with_timescale() {
    local db=$1
    echo "Creating database: $db"
    
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE $db;
EOSQL

    echo "Enabling TimescaleDB extension for $db"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d "$db" <<-EOSQL
        CREATE EXTENSION IF NOT EXISTS timescaledb;
EOSQL

    if [ -f "/backups/$db.sql" ]; then
        echo "Restoring $db from SQL backup"
        psql -U "$POSTGRES_USER" -d "$db" -f "/backups/$db.sql"
    fi
    
    echo "Creating analytics tables in $db"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d "$db" <<-EOSQL
    DROP TABLE IF EXISTS user_events CASCADE;
    
    CREATE TABLE user_events (
        id BIGSERIAL,
        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        user_id INTEGER NOT NULL,
        task_id INTEGER,
        event_type TEXT NOT NULL,
        payload JSONB DEFAULT '{}'::jsonb
    );
    
    ALTER TABLE user_events 
    ADD PRIMARY KEY (user_id, task_id, timestamp);
    
    DO \$\$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM timescaledb_information.hypertables 
            WHERE hypertable_name = 'user_events'
        ) THEN
            PERFORM create_hypertable('user_events', 'timestamp');
        END IF;
    END \$\$;
    
    CREATE INDEX IF NOT EXISTS idx_user_events_user ON user_events(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_events_task ON user_events(task_id) WHERE task_id IS NOT NULL;
    CREATE INDEX IF NOT EXISTS idx_user_events_type ON user_events(event_type);

    CREATE INDEX IF NOT EXISTS idx_user_events_time ON user_events(timestamp DESC);
EOSQL

}

create_db_with_timescale "users_db"

echo "Creating game_db and setting up restricted user"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE game_db;
    
    CREATE USER game_readonly WITH PASSWORD '${GAME_DB_PASSWORD}';
    
    \c game_db
    
    GRANT CONNECT ON DATABASE game_db TO game_readonly;
    
    GRANT USAGE ON SCHEMA public TO game_readonly;
    
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO game_readonly;
    
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO game_readonly;
EOSQL
