-- See https://oktawiki.atlassian.net/wiki/x/yA-ML for this task motivation
--
-- Execute COPY_RAW_EVENTS_TO_EVENTS once every hour
ALTER TASK INFRA.COPY_RAW_EVENTS_TO_EVENTS SET SCHEDULE = 'USING CRON 1 * * * * UTC';

-- Execute RUN_TRIM_OLD_SENSITIVE_DATA 5 minutes after midnight every beginning of a month
ALTER TASK INFRA.RUN_TRIM_OLD_SENSITIVE_DATA SET SCHEDULE = 'USING CRON 5 0 1 * * UTC';

-- Rename the Snowflake provided DEMO_WH to SHARED_WH and change its settings to be more costs efficient
ALTER WAREHOUSE IF EXISTS DEMO_WH RENAME TO SHARED_WH;
ALTER WAREHOUSE IF EXISTS SHARED_WH SET
    WAREHOUSE_SIZE = XSMALL
    AUTO_SUSPEND = 60
    COMMENT = 'Shared warehouse for anyone to use';

-- Drop the Snowflake provided LOAD_WH to avoid confusion
DROP WAREHOUSE IF EXISTS LOAD_WH;
