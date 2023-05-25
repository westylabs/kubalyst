--
-- Setup the infrastructure schema, which contains all objects involved in ELT.
-- E.g. streams on the SENSITIVE.EVENTS table, tasks to copy data between tables,
-- stage, and snowpipe definitions.
--

-- Switch to SYSADMIN who owns all the objects
USE ROLE SYSADMIN;

-- Create a warehouse for loading/transformation purposes
CREATE OR REPLACE WAREHOUSE LOADING_WH
    WITH WAREHOUSE_SIZE = '${elt.warehouse.size}'
    WAREHOUSE_TYPE = 'STANDARD'
    AUTO_SUSPEND = ${elt.warehouse.autoSuspendSeconds}
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'A warehouse for data ELT';

USE DATABASE ${events.database};

CREATE OR REPLACE SCHEMA INFRA
    COMMENT = 'Schema for infrastructure objects like stages, snowpipes, streams, tasks etc';

USE ROLE SECURITYADMIN;

--
-- Setup ELT
--
CREATE OR REPLACE ROLE ${events.role.dataLoader}
    COMMENT = 'Loads data from the landing zone and performs other ELT tasks. It should not be granted to users';

-- DATA_LOADER can use the LOADING warehouse, and read/write from the sensitive schema.
GRANT USAGE ON WAREHOUSE LOADING_WH TO ROLE ${events.role.dataLoader};
GRANT ROLE ${events.role.sensitiveReader} TO ROLE ${events.role.dataLoader};
GRANT ROLE ${events.role.sensitiveWriter} TO ROLE ${events.role.dataLoader};

-- Create a roles hierarchy where all objects are accessible by SYSADMIN
GRANT ROLE ${events.role.dataLoader} TO ROLE SYSADMIN;
GRANT OWNERSHIP ON SCHEMA ${events.database}.INFRA TO ROLE ${events.role.dataLoader};

-- Grant the required privileges to SYSADMIN account to be able to execute tasks
USE ROLE ACCOUNTADMIN;
GRANT EXECUTE TASK ON ACCOUNT TO ROLE ${events.role.dataLoader};

-- Create ELT objects in the 'infra' schema
USE ROLE ${events.role.dataLoader};
USE DATABASE ${events.database};
USE SCHEMA INFRA;

-- Create a stream to track changes in RAW_EVENTS
CREATE OR REPLACE STREAM raw_events_stream ON TABLE SENSITIVE.RAW_EVENTS;

-- Create a task to move records from RAW_EVENTS to EVENTS
-- The top level event fields are extracted into separate columns for easy querying (and performance optimizations)
-- The Object and Array fields are not flattened because it's not clear yet what information is the most commonly used.
CREATE OR REPLACE TASK copy_raw_events_to_events
    WAREHOUSE = LOADING_WH
    SCHEDULE = '1 MINUTE'
WHEN
    SYSTEM$STREAM_HAS_DATA('raw_events_stream')
AS
INSERT INTO SENSITIVE.EVENTS (insertion_timestamp, cell, uuid, timestamp,
    event_type, version, org_id, display_message_entry, severity, client, actor,
    outcome, target,transaction, debug_context, authentication_context, security_context)
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
    raw_json:security_context::object
FROM raw_events_stream WHERE METADATA$ACTION = 'INSERT';

-- Start the task, because it's created 'paused' by default.
ALTER TASK copy_raw_events_to_events RESUME;
