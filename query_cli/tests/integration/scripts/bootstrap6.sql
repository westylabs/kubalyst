-- This is the user used to manage permissions.
-- See https://docs.snowflake.net/manuals/user-guide/security-access-control-considerations.html#using-the-accountadmin-role
USE ROLE SECURITYADMIN;

GRANT DELETE ON ALL TABLES IN SCHEMA ${events.database}.SENSITIVE TO ROLE ${events.role.sensitiveWriter};
GRANT DELETE ON FUTURE TABLES IN SCHEMA ${events.database}.SENSITIVE TO ROLE ${events.role.sensitiveWriter};

USE ROLE ${events.role.dataLoader};
USE DATABASE ${events.database};
USE SCHEMA INFRA;

-- Create a table to store cleanup execution history
CREATE OR REPLACE TABLE SENSITIVE_CLEANUP_HISTORY (
    execution_time TIMESTAMP_LTZ,
    table_name VARCHAR,
    deleted_records NUMBER
)
DATA_RETENTION_TIME_IN_DAYS = 90 -- Maximum allowed
COMMENT = 'Table stores sensitive data cleanup history to facilitate debugging of cleanup executions';

-- Deletes records from EVENTS.SENSITIVE.RAW_EVENTS table
-- Implementation notice:
-- The delete query relies on timestamp of event (when it was emitted) to identify what events to delete
CREATE OR REPLACE PROCEDURE trim_sensitive_raw_events(TIME_VALUE VARCHAR)
    RETURNS VARCHAR
    LANGUAGE JAVASCRIPT
AS
$$
    var stmt = snowflake.createStatement({
        sqlText: "DELETE FROM SENSITIVE.RAW_EVENTS WHERE TO_TIMESTAMP(raw_json:timestamp::string) < TO_TIMESTAMP(:1);",
        binds: [TIME_VALUE]})
    var rs = stmt.execute()
    rs.next()
    var deletedRecords = rs.getColumnValue(1)

    stmt = snowflake.createStatement({
        sqlText: "INSERT INTO SENSITIVE_CLEANUP_HISTORY VALUES (current_timestamp(), 'sensitive.raw_events', ?);",
        binds: [deletedRecords]})
    stmt.execute()

    return "Done"
$$;

-- Deletes records from EVENTS.SENSITIVE.EVENTS table
CREATE OR REPLACE PROCEDURE trim_sensitive_events(TIME_VALUE VARCHAR)
    RETURNS VARCHAR
    LANGUAGE JAVASCRIPT
AS
$$
    var stmt = snowflake.createStatement({sqlText: "DELETE FROM SENSITIVE.EVENTS WHERE timestamp < TO_TIMESTAMP(:1);", binds: [TIME_VALUE]})
    var rs = stmt.execute()
    rs.next()
    var deletedRecords = rs.getColumnValue(1)

    stmt = snowflake.createStatement({
        sqlText: "INSERT INTO SENSITIVE_CLEANUP_HISTORY VALUES (current_timestamp(), 'sensitive.events', ?);",
        binds: [deletedRecords]})
    stmt.execute()

    return "Done"
$$;

-- Deletes sensitive data from all tables older than 1 year
CREATE OR REPLACE PROCEDURE trim_old_sensitive_data()
    RETURNS VARCHAR
    LANGUAGE JAVASCRIPT
AS
$$
    // Calculate the threshold for deletetion for all tables
    var now = new Date()
    now.setFullYear(now.getFullYear() - 1)
    var startTime = now.getTime().toString()

    // [1/2] First trim raw events
    snowflake.createStatement({
        sqlText: "CALL trim_sensitive_raw_events(:1);",
        binds: [startTime]})
    .execute()

    // [2/2] Next trim raw events
    snowflake.createStatement({
        sqlText: "CALL trim_sensitive_events(:1);",
        binds: [startTime]})
    .execute()

    return "Done"
$$;

-- Create a task that executes cleans old sensitive data once a day UTC
CREATE OR REPLACE TASK run_trim_old_sensitive_data
    WAREHOUSE = LOADING_WH
    SCHEDULE = 'USING CRON 30 0 * * * UTC'
AS
CALL trim_old_sensitive_data();

-- Start the task, because it's created 'paused' by default.
ALTER TASK run_trim_old_sensitive_data RESUME;
