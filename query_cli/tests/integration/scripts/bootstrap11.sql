-- Add `metadata` column to `SENSITIVE.EVENTS` table
ALTER TABLE SENSITIVE.EVENTS ADD COLUMN metadata OBJECT;

USE SCHEMA INFRA;

-- Have to recreate task to modify its body
-- This definition recreates a task defined in V3__infra-role-setup.sql migration
-- and with changes done in V10__reduce-tasks-run-frequencies.sql migration
CREATE OR REPLACE TASK COPY_RAW_EVENTS_TO_EVENTS
    WAREHOUSE = LOADING_WH
    SCHEDULE = 'USING CRON 1 * * * * UTC'
WHEN
    SYSTEM$STREAM_HAS_DATA('raw_events_stream')
AS
INSERT INTO SENSITIVE.EVENTS (insertion_timestamp, cell, uuid, timestamp, event_type, version, org_id,
    display_message_entry, severity, client, actor, outcome, target,transaction, debug_context, authentication_context,
    security_context, metadata)
SELECT
    insertion_timestamp,
    cell,
    raw_json:uuid::string,
    to_timestamp(RAW_JSON:timestamp::string),
    raw_json:event_type::string,
    raw_json:version::string,
    raw_json:org_id::string,
    raw_json:display_message_entry::array,
    raw_json:severity::string,
    raw_json:client::object,
    raw_json:actor::object,
    raw_json:outcome::object,
    raw_json:target::array,
    raw_json:transaction::object,
    raw_json:debug_context::object,
    raw_json:authentication_context::object,
    raw_json:security_context::object,
    raw_json:metadata::object
FROM raw_events_stream WHERE METADATA$ACTION = 'INSERT';

-- Start the task, because it's created 'paused' by default.
ALTER TASK copy_raw_events_to_events RESUME;

USE SCHEMA SENSITIVE;

-- Use querying warehouse to populate data to avoid blocking of events transformation.
USE WAREHOUSE DATA_SCIENTIST_QUERYING_WH;

-- Back fill `metadata` column from `raw_events` table.
-- Use only values that are objects.
-- Before array pivoting was introduced in the DataLakeBolt `metadata` contained an array of {key : value} objects.
INSERT INTO events (metadata)
    SELECT raw_json:metadata::object
    FROM raw_events
    WHERE
          raw_json:metadata IS NOT NULL
          AND IS_OBJECT(raw_json:metadata);
