--
-- This is the 2nd part of snowpipe setup, which creates the actual pipe.
--
-- This step can be run *only* after `aws.source.iam.readerArn` IAM role has
-- been updated with the Snowflake AWS account details. Otherwise, the stage
-- creation statement will fail.
--
-- See V4__snowpipe-setup-part-1.sql for description.
--

-- DATA_LOADER role own all the objects in EVENTS.INFRA schema
USE ROLE ${events.role.dataLoader};
USE SCHEMA INFRA;

CREATE OR REPLACE STAGE SYSLOG_V2_EVENTS
    STORAGE_INTEGRATION = events_landing
    URL = '${aws.source.events.s3Path}'
    FILE_FORMAT = (TYPE = 'JSON');

-- Create Pipe to load events
-- When events are loaded `cell` and `org_id` are additionally to the record.
-- Loading is the only time when `cell` can be inferred from the landing zone S3 prefix.
-- `ord_id` is appended to facilitate the GDPR compliance requirements.
-- `insertion_timestamp` is stored in UTC. `CURRENT_TIMESTAMP` return values in
-- the current time zone. Thus, a time zone convertion is required.
CREATE OR REPLACE PIPE load_events_from_landing auto_ingest=true
as
COPY INTO SENSITIVE.RAW_EVENTS (insertion_timestamp, org_id, cell, raw_json)
FROM ( SELECT
    CONVERT_TIMEZONE('UTC', CURRENT_TIMESTAMP())::timestamp_ntz,
    $1:org_id as org_id,
    REGEXP_SUBSTR(METADATA$FILENAME, 'cell=([[:alnum:]]+)/', 1, 1, 'e') as cell,
    $1 as raw_json
FROM @SYSLOG_V2_EVENTS)
FILE_FORMAT = (TYPE = 'JSON');

-- A procedure that refreshes the injest showpipe to load any missing files cause by the unreliable SQS.
-- It checks for the files which were loaded in the last day, and is supposed to be run by a task once a day.
-- See: https://docs.snowflake.net/manuals/user-guide/data-load-snowpipe-auto-s3.html
--
-- Implementation note:
--      Substract additional 5 minutes to ensure that all files are catch sinse the last run.
CREATE OR REPLACE PROCEDURE refresh_snowpipe()
   RETURNS VARCHAR
   LANGUAGE JAVASCRIPT
AS
$$
    var now = new Date()
    now.setDate(now.getDate() - 1)
    now.setMinutes(now.getMinutes() - 5)
    var stmtString = "ALTER PIPE load_events_from_landing REFRESH MODIFIED_AFTER = '" + now.toISOString() + "';"
    var stmt = snowflake.createStatement({sqlText: stmtString})
    stmt.execute()
    return "Done"
$$;

-- Create a task that executes the refresh_snowpipe procedure daily at midnight UTC
CREATE OR REPLACE TASK run_refresh_snowpipe
    WAREHOUSE = LOADING_WH
    SCHEDULE = 'USING CRON 0 0 * * * UTC'
AS
CALL refresh_snowpipe();

-- Start the task, because it's created 'paused' by default.
ALTER TASK run_refresh_snowpipe RESUME;
